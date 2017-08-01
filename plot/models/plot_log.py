# coding=utf-8

from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..managers import PlotLogManager
from .plot import Plot


class PlotLog(BaseUuidModel):
    """A system model to track an RA\'s attempts to confirm a Plot
    (related).
    """

    plot = models.OneToOneField(Plot, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow)

    history = HistoricalRecords()

    objects = PlotLogManager()

    def __str__(self):
        return self.plot.plot_identifier

    def natural_key(self):
        return self.plot.natural_key()
    natural_key.dependencies = ['plot.plot']
