from django.test import TestCase, tag
from model_mommy import mommy

from ..forms import PlotForm, PlotLogEntryForm
from ..models import PlotLog

from ..constants import ACCESSIBLE
from ..models import PlotLogEntry

from .mixins import PlotMixin


class TestForms(PlotMixin, TestCase):

    def test_plot_form(self):
        plot = mommy.prepare_recipe('plot.plot')
        form = PlotForm(data=plot.__dict__)
        self.assertTrue(form.is_valid())

    def test_plot_log_entry_form(self):
        """Add a plot log entry."""
        plot = self.make_confirmed_plot(household_count=1)
        plot_log = PlotLog.objects.get(plot=plot)
        form = PlotLogEntryForm(
            data=dict(
                plot_log=plot_log.id,
                report_datetime=self.get_utcnow(),
                log_status=ACCESSIBLE))
        self.assertTrue(form.is_valid())

    def test_attempt_to_add_many_plot_log_entry_per_day(self):
        """Attempt to add more than one plot log entry in a day."""
        plot = self.make_confirmed_plot(household_count=1)
        plot_log = PlotLog.objects.get(plot=plot)
        plot_log_entry = PlotLogEntry.objects.get(plot_log=plot_log)
        # edit existing
        form = PlotLogEntryForm(
            data=dict(
                plot_log=plot_log.id,
                report_datetime=plot_log_entry.report_datetime,
                log_status=plot_log_entry.log_status),
            instance=plot_log_entry)
        self.assertTrue(form.is_valid())
        form.save()
        # try to add duplicate
        form = PlotLogEntryForm(
            data=dict(
                plot_log=plot_log.id,
                report_datetime=plot_log_entry.report_datetime,
                log_status=plot_log_entry.log_status))
        self.assertFalse(form.is_valid())
