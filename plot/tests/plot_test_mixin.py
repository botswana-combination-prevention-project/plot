# coding=utf-8

from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from ..constants import ACCESSIBLE, RESIDENTIAL_HABITABLE
from ..models import Plot, PlotLog, PlotLogEntry
from ..mommy_recipes import fake
from edc_base.utils import get_utcnow


class PlotTestMixin:

    """A TestMixin class that adds methods specific to Plot processes."""

    def make_plot(self, **options):
        """Returns a plot instance as would be made initially by
        the server."""
        opts = {}
        for field in Plot._meta.get_fields():
            if field.name in options:
                opts.update({field.name: options.get(field.name)})
        try:
            opts['household_count'] = 0
        except KeyError:
            pass
        opts['report_datetime'] = options.get(
            'report_datetime', self.get_utcnow())
        plot = mommy.make_recipe(
            'plot.plot',
            **opts)

        self.assertFalse(plot.confirmed)
        self.assertTrue(plot.accessible)
        return plot

    def confirm_plot(self, plot, **options):
        plot.gps_confirmed_latitude = options.get(
            'gps_confirmed_latitude', fake.confirmed_latitude())
        plot.gps_confirmed_longitude = options.get(
            'gps_confirmed_longitude', fake.confirmed_longitude())

        plot.household_count = options.get('household_count', 0)

        plot.save()

        plot = Plot.objects.get(pk=plot.pk)
        self.assertTrue(plot.confirmed)
        return plot

    def make_confirmed_plot(self, **options):
        """Make an accessible confirmed plot along with a plot log entry."""

        plot = self.make_plot(**options)

        options['report_datetime'] = options.get(
            'report_datetime', self.get_utcnow())

        self.add_plot_log_entry(
            plot=plot, log_status=ACCESSIBLE,
            **options)

        plot.gps_confirmed_latitude = options.get(
            'gps_confirmed_latitude', fake.confirmed_latitude())
        plot.gps_confirmed_longitude = options.get(
            'gps_confirmed_longitude', fake.confirmed_longitude())
        plot.household_count = options.get('household_count', 0)
        plot.status = options.get('status', RESIDENTIAL_HABITABLE)
        plot.time_of_day = 'mornings'
        plot.time_of_week = 'weekdays'
        plot.save()

        plot = Plot.objects.get(pk=plot.pk)
        self.assertTrue(plot.confirmed)
        return plot

    def add_plot_log_entry(self, plot, log_status=None, **options):
        """Returns a plot log entry instance that defaults to an
        accessible plot."""
        log_status = log_status or ACCESSIBLE
        plot_log = PlotLog.objects.get(plot=plot)

        options['report_datetime'] = options.get(
            'report_datetime', get_utcnow())
        try:
            PlotLogEntry.objects.filter(
                plot_log=plot_log,
                report_datetime=options.get(
                    'report_datetime')).order_by(
                        'report_datetime').last()
        except PlotLogEntry.DoesNotExist:
            pass
        else:
            options['report_datetime'] = options.get(
                'report_datetime') + relativedelta(days=1)

        opts = {}
        for field in PlotLogEntry._meta.get_fields():
            if field.name in options:
                opts.update({field.name: options.get(field.name)})

        return mommy.make_recipe(
            'plot.plotlogentry',
            plot_log=plot_log,
            log_status=log_status,
            **opts)
