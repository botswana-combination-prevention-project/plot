# coding=utf-8

import pytz

from django.apps import apps as django_apps
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import options

from edc_constants.constants import CLOSED
from edc_device.constants import CLIENT
from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.exceptions import MapperError
from edc_map.site_mappers import site_mappers

from .exceptions import PlotEnrollmentError, MaxHouseholdsExceededError, PlotIdentifierError

if 'household_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('household_model',)


class PlotIdentifier(ResearchIdentifier):

    template = '{map_code}{sequence}'
    label = 'plot_identifier'


class EnrollmentModelMixin(models.Model):

    def save(self, *args, **kwargs):
        if self.id:
            app_config = django_apps.get_app_config('plot')
            edc_device_app_config = django_apps.get_app_config('edc_device')
            if app_config.permissions.change(edc_device_app_config.role):
                # client may not change htc plots
                if edc_device_app_config.role == CLIENT and self.htc:
                    raise PlotEnrollmentError(
                        'Blocking attempt to modify plot assigned to the HTC campaign. Got {}.'.format(
                            self.plot_identifier))
                # client may not change plots report_datetime past full enrollment date
                if edc_device_app_config.role == CLIENT:
                    if app_config.enrollment.status == CLOSED:
                        mapper_instance = site_mappers.get_mapper(site_mappers.current_map_area)
                        if self.report_datetime > pytz.utc.localize(
                                mapper_instance.current_survey_dates.full_enrollment_date):
                            raise PlotEnrollmentError(
                                'Enrollment for {0} ended on {1}. This plot, and the '
                                'data related to it, may not be modified. '
                                'See site_mappers'.format(
                                    self.community,
                                    mapper_instance.current_survey_dates.full_enrollment_date.strftime('%Y-%m-%d')))
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
        app_config = django_apps.get_app_config('plot')
        edc_device_app_config = django_apps.get_app_config('edc_device')
        if app_config.permissions.add(edc_device_app_config.role):
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


class GpsModelMixin(models.Model):

    gps_degrees_s = models.DecimalField(
        verbose_name='GPS Degrees-South',
        max_digits=10,
        null=True,
        decimal_places=0)

    gps_minutes_s = models.DecimalField(
        verbose_name='GPS Minutes-South',
        max_digits=10,
        null=True,
        decimal_places=4)

    gps_degrees_e = models.DecimalField(
        verbose_name='GPS Degrees-East',
        null=True,
        max_digits=10,
        decimal_places=0)

    gps_minutes_e = models.DecimalField(
        verbose_name='GPS Minutes-East',
        max_digits=10,
        null=True,
        decimal_places=4)

    gps_lon = models.DecimalField(
        verbose_name='longitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_lat = models.DecimalField(
        verbose_name='latitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_target_lon = models.DecimalField(
        verbose_name='target waypoint longitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_target_lat = models.DecimalField(
        verbose_name='target waypoint latitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    def save(self, *args, **kwargs):
        # if user added/updated gps_degrees_[es] and gps_minutes_[es], update gps_lat, gps_lon
        if (self.gps_degrees_e and self.gps_degrees_s and self.gps_minutes_e and self.gps_minutes_s):
            mapper = site_mappers.get_mapper(site_mappers.current_map_area)
            self.gps_lat = mapper.get_gps_lat(self.gps_degrees_s, self.gps_minutes_s)
            self.gps_lon = mapper.get_gps_lon(self.gps_degrees_e, self.gps_minutes_e)
            mapper.verify_gps_location(self.gps_lat, self.gps_lon, MapperError)
            mapper.verify_gps_to_target(self.gps_lat, self.gps_lon, self.gps_target_lat,
                                        self.gps_target_lon, self.target_radius, MapperError,
                                        radius_bypass_instance=self.increase_radius_instance)
            self.distance_from_target = mapper.gps_distance_between_points(
                self.gps_lat, self.gps_lon, self.gps_target_lat, self.gps_target_lon) * 1000
        super(GpsModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
