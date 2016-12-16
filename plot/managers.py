# coding=utf-8

from django.db import models

from bcpp.manager_mixins import BcppSubsetManagerMixin


class PlotManager(BcppSubsetManagerMixin, models.Manager):

    reference_model = 'plot.plot'
    to_reference_model = ['household_structure', 'household', 'plot']

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot_identifier=plot_identifier)


class PlotLogManager(BcppSubsetManagerMixin, models.Manager):

    lookup = ['plot']

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot__plot_identifier=plot_identifier)


class PlotLogEntryManager(BcppSubsetManagerMixin, models.Manager):

    lookup = ['plot_log', 'plot']

    def get_by_natural_key(self, report_datetime, plot_identifier):
        return self.get(report_datetime=report_datetime, plot__plot_identifier=plot_identifier)
