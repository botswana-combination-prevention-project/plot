# coding=utf-8

from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from edc_base_test.mixins.reference_date_mixin import ReferenceDateMixin

from .constants import ACCESSIBLE
from .models import Plot, PlotLog, PlotLogEntry
from .mommy_recipes import fake


class PlotMixin(ReferenceDateMixin):

    def make_plot(self, **options):
        """With defaults makes a plot as would be made initially by the server."""
        plot = mommy.make_recipe(
            'plot.plot',
            report_datetime=self.get_utcnow(),
            **options)
        self.assertFalse(plot.confirmed)
        if plot.htc:
            self.assertFalse(plot.accessible)
        else:
            self.assertTrue(plot.accessible)
        return plot

    def confirm_plot(self, plot, **options):
        plot.gps_confirmed_latitude = options.get('gps_confirmed_latitude', fake.confirmed_latitude())
        plot.gps_confirmed_longitude = options.get('gps_confirmed_longitude', fake.confirmed_longitude())
        plot.household_count = options.get('household_count', 0)
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        self.assertTrue(plot.confirmed)
        return plot

    def make_confirmed_plot(self, **options):
        """Make a accessible confirmed plot along with a plot log entry."""
        plot = self.make_plot()
        self.make_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot.gps_confirmed_latitude = options.get('gps_confirmed_latitude', fake.confirmed_latitude())
        plot.gps_confirmed_longitude = options.get('gps_confirmed_longitude', fake.confirmed_longitude())
        plot.household_count = options.get('household_count', 0)
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        self.assertTrue(plot.confirmed)
        return plot

    def make_plot_log_entry(self, plot=None, report_datetime=None, log_status=None):
        """Make a plot log entry, defaults to an accessible plot."""
        log_status = log_status or ACCESSIBLE
        plot_log = PlotLog.objects.get(plot=plot)
        plot_log_entry = PlotLogEntry.objects.filter(plot_log=plot_log).order_by('report_datetime').last()
        try:
            report_datetime = plot_log_entry.report_datetime + relativedelta(days=1)
        except AttributeError:
            report_datetime = self.get_utcnow() - relativedelta(days=10)
        return mommy.make_recipe(
            'plot.plotlogentry',
            report_datetime=report_datetime,
            plot_log=plot_log,
            log_status=log_status)
