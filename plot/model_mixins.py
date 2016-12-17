# coding=utf-8

from django.apps import apps as django_apps
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import options

from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.site_mappers import site_mappers

from .exceptions import MaxHouseholdsExceededError, PlotIdentifierError, PlotAssignmentError, PlotEnrollmentError
from edc_base.model.validators.date import datetime_not_future


if 'household_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('household_model',)


class PlotIdentifier(ResearchIdentifier):

    template = '{map_code}{sequence}'
    label = 'plot_identifier'


class PlotAssignmentMixin(models.Model):
    """Limit modifications to plots that meet certain criteria, e.g. not an HTC plot."""

    htc = models.BooleanField(
        default=False,
        editable=False)

    enrolled = models.BooleanField(
        default=False,
        editable=False,
        help_text=('a.k.a. bhs, True indicates that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    enrolled_datetime = models.DateTimeField(
        null=True,
        validators=[datetime_not_future],
        editable=False,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    def save(self, *args, **kwargs):
        if self.id:
            if self.htc:
                raise PlotAssignmentError('Plot is assigned to HTC and may not be edited')
        if self.enrolled and not self.enrolled_datetime:
            raise PlotEnrollmentError('Plot requires an enrollment datetime for enrolled=True')
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

    def save(self, *args, **kwargs):
        """Allows a device with permission to allocate a plot identifier to a new instance."""
        if not self.id:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = edc_device_app_config.device_permissions.get(self._meta.label_lower)
            if device_permissions.may_add(edc_device_app_config.role):
                if not self.id:
                    self.plot_identifier = PlotIdentifier(
                        map_code=site_mappers.get_mapper(site_mappers.current_map_area).map_code,
                        study_site=site_mappers.get_mapper(site_mappers.current_map_area).map_code).identifier
            else:
                raise PlotIdentifierError(
                    'Blocking attempt to create plot identifier. Got device \'{}\'.'.format(
                        edc_device_app_config.role))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class CreateHouseholdsModelMixin(models.Model):

    household_count = models.IntegerField(
        verbose_name="Number of Households on this plot.",
        default=0,
        validators=[MaxValueValidator(9)],
        help_text=("Provide the number of households in this plot."))

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
