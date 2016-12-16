from model_mommy import mommy

from edc_base.test_mixins.reference_date_mixin import ReferenceDateMixin

from ..constants import ACCESSIBLE
from ..mommy_recipes import fake

from ..models import Plot, PlotLog
from plot.mommy_recipes import get_utcnow
from plot.models import PlotLogEntry
from dateutil.relativedelta import relativedelta


class PlotMixin(ReferenceDateMixin):

    def make_plot(self, **options):
        """With defaults makes a plot as would be made initially by the server."""
        plot = mommy.make_recipe(
            'plot.plot',
            **options)
        self.assertFalse(plot.confirmed)
        self.assertTrue(plot.accessible)
        return plot

    def make_confirmed_plot(self):
        plot = self.make_plot()
        self.make_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot.gps_confirm_latitude = fake.confirmed_latitude()
        plot.gps_confirm_longitude = fake.confirmed_longitude()
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        self.assertTrue(plot.confirmed)
        return plot

    def make_plot_log_entry(self, plot=None, report_datetime=None, log_status=None):
        log_status = log_status or ACCESSIBLE
        plot_log = PlotLog.objects.get(plot=plot)
        plot_log_entry = PlotLogEntry.objects.filter(plot_log=plot_log).order_by('report_datetime').last()
        try:
            report_datetime = plot_log_entry.report_datetime + relativedelta(days=1)
        except AttributeError:
            report_datetime = get_utcnow() - relativedelta(days=10)
        return mommy.make_recipe(
            'plot.plotlogentry',
            report_datetime=report_datetime,
            plot_log=plot_log,
            log_status=log_status)
