from django.test import TestCase, tag
from django.urls.base import reverse

from edc_dashboard.wrappers import ModelWrapperError, ModelWithLogWrapperError

from ..models import Plot
from ..views.wrappers import PlotWithLogEntryWrapper

from .mixins import PlotMixin
from pprint import pprint


class TestWrappers(PlotMixin, TestCase):

    def setUp(self):
        self.plot = self.make_confirmed_plot()

    @tag('meT')
    def test_plot_wrapper(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)

    @tag('meT')
    def test_plot_wrapper_model_names(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        pprint(wrapped.__dict__)
        self.assertEqual(wrapped.plot, self.plot)

    @tag('meT')
    def test_plot_wrapper_rel_names(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertEqual(wrapped.log_rel_attrs, ['plotlog', 'plotlogentry_set'])

    @tag('me')
    def test_plot_wrapper_aliases(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.log)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertIsNotNone(wrapped.log_entry_set)

    @tag('me')
    def test_plot_wrapper_log_entry_set(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertEqual(self.plot.plotlog.plotlogentry_set.all().count(), 1)
        self.assertEqual(len(wrapped.log_entry_set), 1)

    @tag('me')
    def test_plot_wrapper_log_urls(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.log_entry.add_url_name)
        self.assertIsNotNone(wrapped.log_entry.change_url_name)

    @tag('me')
    def test_plot_wrapper_next_urls(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.log_entry.next_url)
        self.assertIsNotNone(wrapped.log_entry.extra_querystring)

    @tag('me')
    def test_plot_wrapper_urls(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.add_url_name)
        self.assertIsNotNone(wrapped.change_url_name)

    @tag('me')
    def test_plot_wrapper_reverses_urls(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        url_name = wrapped.add_url_name.split('plot:')[1]
        reverse(url_name)
        self.assertIsNotNone(wrapped.change_url_name)
        url_name = wrapped.change_url_name.split('plot:')[1]
        reverse(url_name, args=(wrapped.id,))

    @tag('me')
    def test_plot_wrapper_reverses_log_urls(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        url_name = wrapped.log_entry.add_url_name.split('plot:')[1]
        reverse(url_name)
        url_name = wrapped.log_entry.change_url_name.split('plot:')[1]
        reverse(url_name, args=(wrapped.log_entry.id, ))

    @tag('me')
    def test_does_not_wrap_empty_objects(self):
        class TestEmpty:
            pass
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertRaises(ModelWrapperError, wrapped.object_wrapper, TestEmpty())

    @tag('me')
    def test_wraps_empty_models(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        try:
            wrapped.object_wrapper(Plot())
        except (ModelWithLogWrapperError, ModelWrapperError) as e:
            self.fail('Exception unexpectedly raised. Got{}'.format(str(e)))

    def test_does_not_accept_empty_models(self):
        self.assertRaises(ModelWithLogWrapperError, PlotWithLogEntryWrapper, Plot())

    @tag('me')
    def test_does_not_accept_none(self):
        self.assertRaises(ModelWithLogWrapperError, PlotWithLogEntryWrapper, None)

    @tag('me')
    def test_mock_log_entry_has_attrs(self):
        self.plot.plotlog.plotlogentry_set.all().delete()
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertEqual(wrapped.log_entry.add_url_name, 'plot:plot_admin:plot_plotlogentry_add')
        self.assertEqual(wrapped.log_entry.change_url_name, 'plot:plot_admin:plot_plotlogentry_change')
        self.assertEqual(
            wrapped.log_entry.next_url,
            'plot:listboard_url,plot_identifier&plot_identifier={}'.format(self.plot.plot_identifier))
        self.assertEqual(
            wrapped.log_entry.extra_querystring,
            'plot_log={}'.format(self.plot.plotlog.pk))

    @tag('me1')
    def test_log_entry_has_attrs(self):
        wrapped = PlotWithLogEntryWrapper(self.plot)
        self.assertIsNotNone(wrapped.log_entry)
        self.assertEqual(wrapped.log_entry.add_url_name, 'plot:plot_admin:plot_plotlogentry_add')
        self.assertEqual(wrapped.log_entry.change_url_name, 'plot:plot_admin:plot_plotlogentry_change')
        self.assertEqual(
            wrapped.log_entry.extra_querystring,
            'plot_log={}'.format(self.plot.plotlog.pk))
        self.assertEqual(
            wrapped.log_entry.next_url,
            'plot:listboard_url,plot_identifier&plot_identifier={}'.format(self.plot.plot_identifier))
