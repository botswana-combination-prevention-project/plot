from django.test import TestCase, tag

from edc_map.site_mappers import site_mappers
from edc_model_wrapper import ModelWrapperError, ModelWithLogWrapperError

from ..model_wrappers import PlotWithLogEntryModelWrapper
from ..models import Plot
from .mappers import TestPlotMapper
from .plot_test_mixin import PlotTestMixin


@tag('wrappers')
class TestWrappers(PlotTestMixin, TestCase):

    def setUp(self):
        site_mappers.registry = {}
        site_mappers.register(TestPlotMapper)
        self.plot = self.make_confirmed_plot()

    def test_plot_wrapper(self):
        PlotWithLogEntryModelWrapper(model_obj=self.plot)

    def test_plot_wrapper_model_names(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertEqual(wrapped.object, self.plot)

    def test_plot_wrapper_rel_names(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertTrue(wrapped.log_entry)
        self.assertTrue(wrapped.log_entries)

    def test_plot_wrapper_aliases(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.log)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertIsNotNone(wrapped.log_entries)

    def test_plot_wrapper_log_entries(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertEqual(self.plot.plotlog.plotlogentry_set.all().count(), 1)
        self.assertEqual(len(wrapped.log_entries), 1)

    def test_plot_wrapper_next_urls(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.log_entry.next_url)
        self.assertIsNotNone(wrapped.log_entry.querystring)

    def test_wraps_empty_models(self):
        try:
            PlotWithLogEntryModelWrapper(model_obj=Plot())
        except ModelWrapperError as e:
            self.fail(f'ModelWrapperError unexpectedly raised. Got{e}')

    def test_does_not_accept_none(self):
        self.assertRaises(
            AttributeError, PlotWithLogEntryModelWrapper, model_obj=None)

    def test_mock_log_entry_has_next_url(self):
        self.plot.plotlog.plotlogentry_set.all().delete()
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertEqual(
            wrapped.log_entry.next_url,
            f'plot_dashboard:listboard_url,plot_identifier&plot_identifier='
            f'{self.plot.plot_identifier}')

    def test_mock_log_entry_has_querystring(self):
        self.plot.plotlog.plotlogentry_set.all().delete()
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertEqual(
            wrapped.log_entry.querystring,
            f'plot_log={self.plot.plotlog.pk}')

    def test_log_entry_has_next_url(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertIsNotNone(wrapped.plot_log)
        self.assertIsNotNone(wrapped.plot_log_entry)
        self.assertEqual(
            wrapped.log_entry.next_url,
            f'plot_dashboard:listboard_url,plot_identifier&plot_identifier='
            f'{self.plot.plot_identifier}')

    def test_log_entry_has_querystring(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.log_entry.id)
        self.assertEqual(
            wrapped.log_entry.querystring,
            f'plot_log={self.plot.plotlog.pk}')

    def test_wrapper_fields(self):
        wrapped = PlotWithLogEntryModelWrapper(model_obj=self.plot)
        self.assertIsNotNone(wrapped.map_area)
        self.assertIsNotNone(wrapped.created)
        self.assertIsNotNone(wrapped.modified)
        self.assertIsNotNone(wrapped.confirmed)
