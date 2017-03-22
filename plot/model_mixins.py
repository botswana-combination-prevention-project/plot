# coding=utf-8

from django.apps import apps as django_apps
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import options
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

from edc_dashboard.model_mixins import SearchSlugModelMixin as BaseSearchSlugModelMixin
from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.exceptions import MapperError
from edc_map.site_mappers import site_mappers

from .choices import SELECTED
from .constants import TWENTY_PERCENT, FIVE_PERCENT
from .exceptions import (
    MaxHouseholdsExceededError, PlotIdentifierError,
    PlotConfirmationError, PlotEnrollmentError,
    CreateHouseholdError, PlotCreateError)


if 'household_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('household_model',)


class PlotIdentifier(ResearchIdentifier):

    template = '{map_code}{sequence}'
    label = 'plot_identifier'


class SearchSlugModelMixin(BaseSearchSlugModelMixin):

    def get_slugs(self):
        slugs = super().get_slugs()
        return slugs + [
            self.plot_identifier or '',
            self.map_area or '',
            self.cso_number or '',
        ]

    class Meta:
        abstract = True


class PlotConfirmationMixin(models.Model):

    def common_clean(self):
        if not self.id:
            if (self.gps_confirmed_latitude or
                    self.gps_confirmed_longitude) and not self.ess:
                raise PlotConfirmationError(
                    'Blocking attempt to confirm non-ESS plot on add.')
        else:
            if self.gps_confirmed_latitude and self.gps_confirmed_longitude:
                self.get_confirmed()
                try:
                    PlotLog = django_apps.get_model(*'plot.plotlog'.split('.'))
                    PlotLog.objects.get(plot__pk=self.id)
                except PlotLog.DoesNotExist:
                    app_config = django_apps.get_app_config('plot')
                    if app_config.excluded_plot(self):
                        # excluded plots are not normal plots to
                        # be surveyed, dont allow confirmation
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. Got plot logs '
                            'are not created for excluded plots.')
                    else:
                        # add Plot -> signal creates PlotLog, -> user
                        # creates PlotLogEntry -> user may update Plot
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. '
                            'Got plot log not created.')
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    # once enrolled, dont allow modification to GPS
                    raise PlotEnrollmentError(
                        'Plot cannot be unconfirmed. Got plot is '
                        'already enrolled.')
        return super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [PlotConfirmationError]

    class Meta:
        abstract = True


class PlotEnrollmentMixin(models.Model):

    htc = models.BooleanField(
        default=False,
        editable=False)

    ess = models.BooleanField(
        default=False,
        blank=True,
        help_text=('True if plot is part of ESS and outside of '
                   'plots randomly selected'))

    rss = models.BooleanField(
        editable=False,
        default=False,
        help_text=('True if plot is one of those randomly '
                   'selected. See plot.selected'))

    selected = models.CharField(
        max_length=25,
        verbose_name='selected',
        choices=SELECTED,
        editable=False,
        null=True,
        help_text=(
            '1=20% of selected plots, 2=additional 5% selected '
            'buffer/pool, None=75%'))

    enrolled = models.BooleanField(
        default=False,
        help_text=('True indicates that plot is enrolled into a survey. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    enrolled_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    def common_clean(self):
        if self.htc and self.selected in [TWENTY_PERCENT, FIVE_PERCENT]:
            if self.enrolled:
                raise PlotEnrollmentError(
                    'Plot cannot be enrolled. Plot cannot be assigned '
                    'to both HTC and RSS.')
            else:
                raise PlotCreateError('Plot cannot be assigned to both '
                                      'HTC and RSS.')
        if self.ess and any([self.htc, self.rss, self.selected]):
            raise PlotEnrollmentError(
                'Plot cannot be an ESS plot. Check value of RSS, HTC '
                'or \'selected\'.')
        if self.htc and not self.ess and self.enrolled:
            raise PlotEnrollmentError(
                'Plot cannot be enrolled. Got plot is assigned to HTC.')
        if self.enrolled and not self.enrolled_datetime:
            raise PlotEnrollmentError(
                'Plot cannot be enrolled. Got '
                'plot requires an enrolled datetime.')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [
            PlotEnrollmentError, PlotCreateError]

    def save(self, *args, **kwargs):
        self.rss = True if self.selected in [
            TWENTY_PERCENT, FIVE_PERCENT] else False
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class PlotIdentifierModelMixin(models.Model):
    """Mixin to allocate a plot identifier.
    """

    plot_identifier = models.CharField(
        verbose_name='Plot Identifier',
        max_length=25,
        unique=True,
        editable=False)

    def common_clean(self):
        """Block a device without permissions from allocating a
        plot identifier to a new instance.
        """
        if not self.id and not self.plot_identifier:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = (
                edc_device_app_config.device_permissions.get(
                    self._meta.label_lower))
            if not device_permissions.may_add(edc_device_app_config.role):
                raise PlotIdentifierError(
                    'Blocking attempt to create plot identifier. '
                    'Got device \'{}\'.'.format(
                        edc_device_app_config.role))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [PlotIdentifierError]

    def save(self, *args, **kwargs):
        """Allocates a plot identifier to a new instance if
        permissions allow.
        """
        if not self.id and not self.plot_identifier:
            edc_device_app_config = django_apps.get_app_config(
                'edc_device')
            device_permissions = (
                edc_device_app_config.device_permissions.get(
                    self._meta.label_lower))
            if device_permissions.may_add(edc_device_app_config.role):
                if not self.id:
                    self.plot_identifier = PlotIdentifier(
                        map_code=site_mappers.get_mapper(
                            self.map_area).map_code,
                        study_site=site_mappers.get_mapper(
                            self.map_area).map_code).identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CreateHouseholdsModelMixin(models.Model):

    household_count = models.IntegerField(
        verbose_name="Number of Households on this plot.",
        default=0,
        validators=[MaxValueValidator(9)],
        help_text=("Provide the number of households in this plot."))

    def common_clean(self):
        if not (self.gps_confirmed_longitude and self.gps_confirmed_latitude):
            if self.household_count > 0:
                raise CreateHouseholdError(
                    'Households cannot exist on a unconfirmed plot. '
                    'Got household count = {}. Perhaps add the '
                    'confirmation GPS point.'.format(
                        self.household_count))
            if self.eligible_members > 0:
                raise CreateHouseholdError(
                    'Households cannot exist on a unconfirmed plot. '
                    'Got eligible_members eligible_members = '
                    '{}'.format(self.eligible_members))
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [
            CreateHouseholdError, MaxHouseholdsExceededError]

    def create_or_delete_households(self):
        """Creates or deletes households to try to equal the
        household_count.

        Delete will fail if household has data upstream.
        """
        app_config = django_apps.get_app_config('plot')

        if self.household_count > app_config.max_households:
            raise MaxHouseholdsExceededError(
                'Number of households per plot cannot exceed {}. '
                'See plot.AppConfig'.format(app_config.max_households))

        if self.gps_confirmed_longitude and self.gps_confirmed_latitude:
            Household = django_apps.get_model(
                *self._meta.household_model.split('.'))
            households = Household.objects.filter(plot=self)
            to_delete = households.count() - self.household_count

            if to_delete > 0:
                for household in households:
                    self.safe_delete(household)
                    to_delete -= 1
                    if not to_delete:
                        break
            elif households.count() < self.household_count:
                self.create_households()

            self.household_count = Household.objects.filter(
                plot__id=self.id).count()
            self.save(update_fields=['household_count'])

    def create_households(self):
        Household = django_apps.get_model(
            *self._meta.household_model.split('.'))
        for n in range(1, self.household_count + 1):
            with transaction.atomic():
                try:
                    Household.objects.create(
                        plot=self,
                        household_sequence=n,
                        report_datetime=self.report_datetime)
                except IntegrityError:
                    pass

    def safe_delete(self, household):
        """Safe delete households passing on ProtectedErrors.
        """
        HouseholdLog = django_apps.get_model('household.householdlog')
        HouseholdStructure = django_apps.get_model(
            'household.householdstructure')
        household_structures = HouseholdStructure.objects.filter(
            household=household)
        for household_structure in household_structures:
            try:
                for household_log in HouseholdLog.objects.filter(
                        household_structure=household_structure):
                    household_log.delete()
                    household_structure.delete()
                    household.delete()
            except ProtectedError:
                pass

    class Meta:
        abstract = True
        household_model = None
