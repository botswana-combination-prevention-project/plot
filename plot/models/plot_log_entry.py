# coding=utf-8

import arrow

from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields import EncryptedTextField

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow

from ..choices import PLOT_LOG_STATUS, INACCESSIBILITY_REASONS
from ..managers import PlotLogEntryManager
from .plot_log import PlotLog


class PlotLogEntry(BaseUuidModel):
    """A model completed by the user to track an RA\'s attempts to
    confirm a Plot.
    """

    plot_log = models.ForeignKey(PlotLog, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        validators=[datetime_not_future],
        # TODO: get this validator to work
        # validators=[datetime_not_future, date_in_survey_for_map_area],
        default=get_utcnow)

    report_date = models.DateField(
        editable=False,
        help_text='date value of report_datetime for unique constraint')

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
        help_text=('IMPORTANT: Do not include any names or other '
                   'personally identifying '
                   'information in this comment'))

    objects = PlotLogEntryManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.report_date = arrow.Arrow.fromdatetime(
            self.report_datetime, self.report_datetime.tzinfo).to('utc').date()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.report_datetime, ) + self.plot_log.natural_key()
    natural_key.dependencies = ['plot.plot_log']

    def __str__(self):
        return '{} ({})'.format(
            self.plot_log, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        app_label = 'plot'
        unique_together = ('plot_log', 'report_datetime')
        ordering = ('report_datetime', )
