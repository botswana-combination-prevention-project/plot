# coding=utf-8

from django.apps import apps as django_apps
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import options

from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.site_mappers import site_mappers

from .exceptions import (
    MaxHouseholdsExceededError, PlotIdentifierError, PlotConfirmationError, PlotEnrollmentError,
    CreateHouseholdError)
from edc_map.exceptions import MapperError


if 'household_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('household_model',)


class PlotIdentifier(ResearchIdentifier):

    template = '{map_code}{sequence}'
    label = 'plot_identifier'


class PlotConfirmationMixin(models.Model):

    def common_clean(self):
        if not self.id and (self.gps_confirmed_latitude or self.gps_confirmed_longitude):
            raise PlotConfirmationError('Blocking attempt to confirm plot on add.')
        if self.id:
            if self.gps_confirmed_latitude and self.gps_confirmed_longitude:
                self.get_confirmed()
                try:
                    PlotLog = django_apps.get_model(*'plot.plotlog'.split('.'))
                    PlotLog.objects.get(plot__pk=self.id)
                except PlotLog.DoesNotExist:
                    app_config = django_apps.get_app_config('plot')
                    if app_config.excluded_plot(self):
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. Got plot logs are not created for excluded plots.')
                    else:
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. Got plot log not created.')
                if self.htc:
                    raise PlotConfirmationError('Plot cannot be confirmed. Got plot is assigned to HTC.')
                if not self.accessible:
                    raise PlotConfirmationError('Plot cannot be confirmed. Got plot is inaccessible.')
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    raise PlotEnrollmentError('Plot cannot be unconfirmed. Got plot is already enrolled.')
        super().common_clean()

    class Meta:
        abstract = True


class PlotEnrollmentMixin(models.Model):
    """Limit modifications to plots that meet certain criteria, e.g. not an HTC plot."""

    htc = models.BooleanField(
        default=False)

    enrolled = models.BooleanField(
        default=False,
        help_text=('a.k.a. bhs, True indicates that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    enrolled_datetime = models.DateTimeField(
        null=True,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    def common_clean(self):
        if self.id:
            if self.htc and self.enrolled:
                raise PlotEnrollmentError('Plot cannot be enrolled. Got plot is assigned to HTC.')
            if self.enrolled and not self.enrolled_datetime:
                raise PlotEnrollmentError('Plot cannot be enrolled. Got plot requires an enrolled datetime.')
        super().common_clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class PlotIdentifierModelMixin(models.Model):
    """Mixin to allocate a plot identifier."""

    plot_identifier = models.CharField(
        verbose_name='Plot Identifier',
        max_length=25,
        unique=True,
        editable=False)

    def common_clean(self):
        """Allows a device with permission to allocate a plot identifier to a new instance."""
        if not self.id:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = edc_device_app_config.device_permissions.get(self._meta.label_lower)
            if not device_permissions.may_add(edc_device_app_config.role):
                raise PlotIdentifierError(
                    'Blocking attempt to create plot identifier. Got device \'{}\'.'.format(
                        edc_device_app_config.role))
        super().common_clean()

    def save(self, *args, **kwargs):
        if not self.id:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = edc_device_app_config.device_permissions.get(self._meta.label_lower)
            if device_permissions.may_add(edc_device_app_config.role):
                if not self.id:
                    self.plot_identifier = PlotIdentifier(
                        map_code=site_mappers.get_mapper(site_mappers.current_map_area).map_code,
                        study_site=site_mappers.get_mapper(site_mappers.current_map_area).map_code).identifier
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
                    'Got household count = {}'.format(self.household_count))
            if self.eligible_members > 0:
                raise CreateHouseholdError(
                    'Households cannot exist on a unconfirmed plot. '
                    'Got eligible_members eligible_members = {}'.format(self.eligible_members))
        super().common_clean()

    def create_or_delete_households(self):
        """Creates or deletes households to try to equal the number of households reported on the plot instance.

            * households are deleted as long as there are no household members
              and the household log does not have entries.
            * bcpp_clinic is a special case to allow for a plot to represent the BCPP Clinic."""
        app_config = django_apps.get_app_config('plot')
        if self.household_count > app_config.max_households:
            raise MaxHouseholdsExceededError(
                'Number of households per plot cannot exceed {}. '
                'See plot.AppConfig'.format(app_config.max_households))
        if self.gps_confirmed_longitude and self.gps_confirmed_latitude:
            Household = django_apps.get_model(*self._meta.household_model.split('.'))
            households = Household.objects.filter(plot=self)
            to_delete = households.count() - self.household_count
            if to_delete > 0:
                for household in households:
                    household.delete()
                    to_delete -= 1
                    if not to_delete:
                        break
            elif households.count() < self.household_count:
                for n in range(1, (self.household_count - households.count()) + 1):
                    Household.objects.create(plot=self, household_sequence=n)

    class Meta:
        abstract = True
        household_model = None
