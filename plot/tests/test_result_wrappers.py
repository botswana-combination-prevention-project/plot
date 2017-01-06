from django.test import TestCase, tag

from plot.tests.mixins import PlotMixin
from plot.views.plots_view import PlotResultWrapper


class TestWrappers(PlotMixin, TestCase):

    @tag('me')
    def test_plot_wrapper(self):
        plot = self.make_confirmed_plot()
        wrapped = PlotResultWrapper(plot)
        self.assertEqual(wrapped.plot_identifier, plot.plot_identifier)
        self.assertIsNotNone(wrapped.plot_log)
        self.assertIsNotNone(wrapped.plot_log_entry)
        self.assertIsNotNone(wrapped.plot_log_entries)
