from django.apps import apps as django_apps
from django.test import TestCase
from dateutil.relativedelta import relativedelta

from edc_base.utils import get_utcnow

from ..constants import ACCESSIBLE

from .mixins import PlotMixin
from ..view_mixins import PlotLogEntryViewMixin


class TestPlotLogEntryViewMixin(PlotMixin, TestCase):
    """Assert permissions / roles that can create plots."""

    def setUp(self):
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)

    def test_not_required_plot_log_entry(self):
        """ if plot log entry was added for today, then you cannot add another for the same day."""
        plot = self.make_plot()
        self.make_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        self.assertFalse(plot.confirmed)
        plot_log_entry_view_mixin = PlotLogEntryViewMixin()
        self.assertFalse(plot_log_entry_view_mixin.is_required(plot))

    def test_required_plot_log_entry(self):
        """ if there is no plot log entry, it can be added"""
        plot = self.make_plot()
        self.assertFalse(plot.confirmed)
        plot_log_entry_view_mixin = PlotLogEntryViewMixin()
        self.assertTrue(plot_log_entry_view_mixin.is_required(plot))

    def test_required_plot_log_entry_valid1(self):
        """ For a confirm plot, plot log entry is not required."""
        plot = self.make_plot()
        plot = self.confirm_plot(plot)
        plot.household_count = 3
        plot.save()
        self.assertTrue(plot.confirmed)
        plot_log_entry_view_mixin = PlotLogEntryViewMixin()
        self.assertFalse(plot_log_entry_view_mixin.is_required(plot))

    def test_notrequired_plot_log_entry1(self):
        """ if there are three plot log entry, then the fourth one is not required."""
        plot = self.make_plot()
        self.assertFalse(plot.confirmed)
        for day in [get_utcnow() + relativedelta(days=i) for i in range(3)]:
            self.make_plot_log_entry(plot=plot, report_datetime=day, log_status=ACCESSIBLE)
        plot_log_entry_view_mixin = PlotLogEntryViewMixin()
        self.assertFalse(plot_log_entry_view_mixin.is_required(plot))
