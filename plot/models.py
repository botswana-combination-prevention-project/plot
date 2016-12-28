# coding=utf-8

from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.utils import get_utcnow
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_map.model_mixins import MapperModelMixin
from edc_map.exceptions import MapperError
from edc_device.model_mixins import DeviceModelMixin
from edc_base.model.validators.date import datetime_not_future

from survey.validators import date_in_survey

from .choices import PLOT_STATUS, SELECTED, PLOT_LOG_STATUS, INACCESSIBILITY_REASONS
from .exceptions import PlotEnrollmentError
from .model_mixins import (
    PlotIdentifierModelMixin, CreateHouseholdsModelMixin, PlotEnrollmentMixin, PlotConfirmationMixin)
from plot.constants import INACCESSIBLE
from django.core.exceptions import MultipleObjectsReturned
from plot.managers import PlotManager, PlotLogManager, PlotLogEntryManager
from edc_map.site_mappers import site_mappers


class Plot(MapperModelMixin, DeviceModelMixin, PlotIdentifierModelMixin, PlotEnrollmentMixin,
           PlotConfirmationMixin, CreateHouseholdsModelMixin, BaseUuidModel):
    """A model created by the system and updated by the user to represent a Plot
    in the community."""

    report_datetime = models.DateTimeField(
        validators=[datetime_not_future],
        default=get_utcnow)

    eligible_members = models.IntegerField(
        verbose_name="Approximate number of age eligible members",
        default=0,
        null=True,
        help_text=(("Provide an approximation of the number of people "
                    "who live in this residence who are age eligible.")))

    cso_number = EncryptedCharField(
        verbose_name="CSO Number",
        blank=True,
        null=True,
        help_text=("provide the CSO number or leave BLANK."))

    time_of_week = models.CharField(
        verbose_name='Time of week when most of the eligible members will be available',
        max_length=25,
        choices=TIME_OF_WEEK,
        blank=True,
        null=True)

    time_of_day = models.CharField(
        verbose_name='Time of day when most of the eligible members will be available',
        max_length=25,
        choices=TIME_OF_DAY,
        blank=True,
        null=True)

    status = models.CharField(
        verbose_name='Plot status',
        max_length=35,
        choices=PLOT_STATUS)

    description = EncryptedTextField(
        verbose_name="Description of plot/residence",
        max_length=250,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        null=True)

    selected = models.CharField(
        max_length=25,
        null=True,
        verbose_name='selected',
        choices=SELECTED,
        editable=True,
        help_text=(
            "1=20% of selected plots, 2=additional 5% selected buffer/pool, None=75%"))

    accessible = models.BooleanField(
        default=True,
        editable=False)

    access_attempts = models.IntegerField(
        default=0,
        help_text='Number of attempts to access a plot to determine it\'s status.',
        editable=False)

    objects = PlotManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(self.location_name or 'undetermined', self.plot_identifier)

    def save(self, *args, **kwargs):
        if self.id and not self.location_name:
            self.location_name = 'plot'
        if self.status == INACCESSIBLE:
            self.accessible = False
        elif self.htc:
            self.accessible = False
        else:
            if self.id:
                try:
                    PlotLogEntry.objects.get(plot_log__plot__pk=self.id)
                except PlotLogEntry.DoesNotExist:
                    self.accessible = True
                except MultipleObjectsReturned:
                    pass
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.plot_identifier, )

    def common_clean(self):
        if self.map_area not in site_mappers.map_areas:
            msg = 'Invalid map area. Valid map areas are %(map_areas)s. Got %(map_area)s'
            params = {'map_area': self.map_area, 'map_areas': ', '.join(site_mappers.map_areas)}
            field = 'map_area'
            raise MapperError(msg.format(**params), field, params, msg)
        if self.id:
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    raise PlotEnrollmentError('Plot is enrolled and may not be unconfirmed')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        common_clean_exceptions = super().common_clean_exceptions
        common_clean_exceptions.extend([PlotEnrollmentError, MapperError])
        return common_clean_exceptions

    @property
    def identifier_segment(self):
        return self.plot_identifier[:-3]

    @property
    def community(self):
        return self.map_area

    class Meta:
        app_label = 'plot'
        ordering = ['-plot_identifier', ]
        unique_together = (('gps_target_lat', 'gps_target_lon'),)
        household_model = 'household.household'


class PlotLog(BaseUuidModel):
    """A system model to track an RA\'s attempts to confirm a Plot (related)."""

    plot = models.OneToOneField(Plot, on_delete=PROTECT)

    history = HistoricalRecords()

    objects = PlotLogManager()

    def __str__(self):
        return str(self.plot)

    def natural_key(self):
        return self.plot.natural_key()
    natural_key.dependencies = ['plot.plot']

    class Meta:
        app_label = 'plot'


class PlotLogEntry(BaseUuidModel):
    """A model completed by the user to track an RA\'s attempts to confirm a Plot."""

    plot_log = models.ForeignKey(PlotLog, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        # TODO: get this validator to work
        # validators=[datetime_not_future, date_in_survey_for_map_area],
        default=get_utcnow)

    log_status = models.CharField(
        verbose_name='What is the status of this plot?',
        max_length=25,
        choices=PLOT_LOG_STATUS)

    reason = models.CharField(
        verbose_name='If inaccessible, please indicate the reason.',
        max_length=25,
        blank=True,
        null=True,
        choices=INACCESSIBILITY_REASONS)

    reason_other = models.CharField(
        verbose_name='If Other, specify',
        max_length=100,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        verbose_name="Comments",
        max_length=250,
        null=True,
        blank=True,
        help_text=('IMPORTANT: Do not include any names or other personally identifying '
                   'information in this comment'))

    objects = PlotLogEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.plot_log.natural_key()
    natural_key.dependencies = ['plot.plot_log']

    def __str__(self):
        return '{} ({})'.format(self.plot_log, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        app_label = 'plot'
        unique_together = ('plot_log', 'report_datetime')
        ordering = ('report_datetime', )
