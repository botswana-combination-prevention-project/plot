# coding=utf-8

from django.db import models


class PlotManager(models.Manager):

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot_identifier=plot_identifier)


class PlotLogManager(models.Manager):

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot__plot_identifier=plot_identifier)


class PlotLogEntryManager(models.Manager):

    def get_by_natural_key(self, report_datetime, plot_identifier):
        return self.get(report_datetime=report_datetime,
                        plot__plot_identifier=plot_identifier)
