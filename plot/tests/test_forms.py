# see module plot-forms-validators

from django.apps import apps as django_apps
from django.test import TestCase

from edc_map.site_mappers import site_mappers

from ..forms import PlotForm, PlotLogForm, PlotLogEntryForm
from ..models import Plot, PlotLog, PlotLogEntry
from .plot_test_helper import PlotTestHelper
from .mappers import TestPlotMapper


class TestForms(TestCase):

    plot_helper = PlotTestHelper()

    def setUp(self):
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestPlotMapper)
        self.plot = self.plot_helper.make_plot(htc=True, selected=None)

    def test_plot_form_persisted(self):
        form = PlotForm(data=self.plot.__dict__, instance=self.plot)
        self.assertFalse(form.is_valid())

    def test_plot_form(self):
        form = PlotForm(instance=Plot())
        self.assertFalse(form.is_valid())

    def test_plot_log_form_persisted(self):
        plot_log = PlotLog.objects.create(plot=self.plot)
        form = PlotLogForm(data=plot_log.__dict__, instance=plot_log)
        self.assertFalse(form.is_valid())

    def test_plot_log_form(self):
        plot_log = PlotLog.objects.create(plot=self.plot)
        form = PlotLogForm(data=plot_log.__dict__)
        self.assertFalse(form.is_valid())

    def test_plot_log_entry_form_persisted(self):
        plot_log = PlotLog.objects.create(plot=self.plot)
        plot_log_entry = PlotLogEntry.objects.create(plot_log=plot_log)
        form = PlotLogEntryForm(instance=plot_log_entry)
        self.assertFalse(form.is_valid())

    def test_plot_log_entry_form(self):
        plot_log = PlotLog.objects.create(plot=self.plot)
        plot_log_entry = PlotLogEntry.objects.create(plot_log=plot_log)
        form = PlotLogEntryForm(data=plot_log_entry.__dict__)
        self.assertFalse(form.is_valid())
