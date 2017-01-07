from django.apps import apps as django_apps
from django.test import TestCase, tag
from model_mommy import mommy

from ..forms import PlotForm, PlotLogEntryForm
from ..models import PlotLog

from ..constants import ACCESSIBLE, RESIDENTIAL_HABITABLE, RESIDENTIAL_NOT_HABITABLE
from ..models import PlotLogEntry
from ..mommy_recipes import fake

from .mixins import PlotMixin


class TestFormsNoAdd(PlotMixin, TestCase):

    def setUp(self):
        self.add_plot_map_areas = django_apps.app_configs['plot'].add_plot_map_areas
        django_apps.app_configs['plot'].add_plot_map_areas = []

    def tearDown(self):
        django_apps.app_configs['plot'].add_plot_map_areas = self.add_plot_map_areas

    def test_cannot_add_plot_form_if_not_allowed(self):
        plot = mommy.prepare_recipe(
            'plot.plot',
            ess=True,
            status=RESIDENTIAL_HABITABLE,
            gps_confirmed_latitude=fake.confirmed_latitude,
            gps_confirmed_longitude=fake.confirmed_longitude,
        )
        form = PlotForm(data=plot.__dict__)
        self.assertFalse(form.is_valid())


class TestForms(PlotMixin, TestCase):

    def test_add_ess_plot_form(self):
        plot = mommy.prepare_recipe(
            'plot.plot',
            ess=True,
            status=RESIDENTIAL_HABITABLE,
            time_of_week='weekdays',
            time_of_day='morning',
            household_count=1,
            eligible_members=1,
            gps_confirmed_latitude=fake.confirmed_latitude,
            gps_confirmed_longitude=fake.confirmed_longitude,
        )
        form = PlotForm(data=plot.__dict__)
        self.assertTrue(form.is_valid())

    def test_cannot_add_non_ess_plot_form(self):
        plot = mommy.prepare_recipe(
            'plot.plot',
            ess=False,
            status=RESIDENTIAL_HABITABLE,
            time_of_week='weekdays',
            time_of_day='morning',
            household_count=1,
            eligible_members=1,
            gps_confirmed_latitude=fake.confirmed_latitude,
            gps_confirmed_longitude=fake.confirmed_longitude,
        )
        form = PlotForm(data=plot.__dict__)
        self.assertFalse(form.is_valid())

    def test_cannot_add_non_ess_non_residential_plot_form(self):
        plot = mommy.prepare_recipe(
            'plot.plot',
            ess=True,
            status=RESIDENTIAL_NOT_HABITABLE,
            gps_confirmed_latitude=fake.confirmed_latitude,
            gps_confirmed_longitude=fake.confirmed_longitude,
        )
        form = PlotForm(data=plot.__dict__)
        self.assertFalse(form.is_valid())

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
