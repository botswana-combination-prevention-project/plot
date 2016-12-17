# coding=utf-8

from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_base.utils import get_utcnow
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_map.site_mappers import site_mappers
from edc_map.model_mixins import MapperModelMixin
from edc_map.exceptions import MapperError
from edc_device.model_mixins import DeviceModelMixin
from edc_base.model.validators.date import datetime_not_future

from survey.validators import date_in_survey

from .choices import PLOT_STATUS, SELECTED, PLOT_LOG_STATUS, INACCESSIBILITY_REASONS
from .exceptions import PlotEnrollmentError
from .model_mixins import PlotIdentifierModelMixin, CreateHouseholdsModelMixin, PlotAssignmentMixin


class Plot(MapperModelMixin, DeviceModelMixin, PlotIdentifierModelMixin, PlotAssignmentMixin,
           CreateHouseholdsModelMixin, BaseUuidModel):
    """A model created by the system and updated by the user to represent a Plot
    in the community."""

    report_datetime = models.DateTimeField(
        validators=[datetime_not_future],
        default=get_utcnow,
        editable=False)

    eligible_members = models.IntegerField(
        verbose_name="Approximate number of age eligible members",
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

    # 20 percent plots is reperesented by 1 and 5 percent of by 2, the rest of
    # the plots which is 75 percent selected value is None
    selected = models.CharField(
        max_length=25,
        null=True,
        verbose_name='selected',
        choices=SELECTED,
        editable=False)

    accessible = models.BooleanField(
        default=True,
        editable=False)

    access_attempts = models.IntegerField(
        default=0,
        help_text='Number of attempts to access a plot to determine it\'s status.',
        editable=False)

    # objects = PlotManager()

    history = HistoricalRecords()

    def __str__(self):
        if site_mappers.get_mapper(site_mappers.current_map_area).clinic_plot_identifier == self.plot_identifier:
            return 'BCPP-CLINIC'
        else:
            return self.plot_identifier

    def natural_key(self):
        return (self.plot_identifier, )

    def save(self, *args, **kwargs):
        if self.id:
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    raise PlotEnrollmentError('Plot is enrolled and may not be uncomfirmed')
        super().save(*args, **kwargs)

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

    # objects = PlotLogManager()

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
        validators=[datetime_not_future, date_in_survey],
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

    # objects = PlotLogEntryManager()

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
