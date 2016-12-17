from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.test.utils import override_settings
from model_mommy import mommy

from edc_device.constants import CLIENT, CENTRAL_SERVER
from edc_map.exceptions import MapperError
from edc_map.validators import is_valid_map_area

from household.models import Household

from ..constants import RESIDENTIAL_HABITABLE, INACCESSIBLE
from ..exceptions import PlotIdentifierError, MaxHouseholdsExceededError
from ..models import Plot
from ..mommy_recipes import fake

from .test_mixins import PlotMixin


class TestPlotCreatePermissions(PlotMixin, TestCase):
    """Assert permissions / roles that can create plots."""

    def setUp(self):
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)

    @override_settings(DEVICE_ID='99')
    def test_create_plot_server(self):
        """Asserts a plot may be created by a server."""
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CENTRAL_SERVER)
        try:
            self.make_plot()
        except PlotIdentifierError:
            self.fail('PlotIdentifierError unexpectedly raised')

    @override_settings(DEVICE_ID='00')
    def test_create_plot_client(self):
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CLIENT)
        self.assertRaises(PlotIdentifierError, self.make_plot)

    @override_settings(DEVICE_ID='99')
    def test_create_plot_htc(self):
        """Assert cannot confirm an HTC assigned plot."""
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)
        plot = self.make_plot(htc=True)
        django_apps.app_configs['edc_device'].device_id = '00'
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CLIENT)
        plot.gps_confirmed_latitude = fake.confirmed_latitude()
        plot.gps_confirmed_longitude = fake.confirmed_longitude()
        plot.save()


class TestPlotCreateCommunity(TestCase):

    def test_community_validator(self):
        self.assertRaises(ValidationError, is_valid_map_area, 'wrong_community')
        try:
            is_valid_map_area('test_community')
        except ValidationError:
            self.fail('ValidationError unexpectedly raised')


@override_settings(DEVICE_ID='99')
class TestPlot(PlotMixin, TestCase):

    def setUp(self):
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)

    def test_plot_creates_household(self):
        """Assert creating a plot with a household count creates that many households"""
        plot = self.make_plot(household_count=1)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)
        plot = self.make_plot(household_count=2)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 2)
        plot = self.make_plot(household_count=3)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

    def test_plot_add_subtract_household(self):
        """Assert change number of households will delete and recreate."""
        plot = self.make_plot(household_count=3)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)
        plot.household_count = 2
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 2)
        plot.household_count = 1
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)

    def test_plot_creates_no_households(self):
        plot = self.make_plot(household_count=0)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 0)

    def test_plot_add_too_many_households(self):
        """Assert cannot exceed max plots."""
        self.assertRaises(MaxHouseholdsExceededError, self.make_plot, household_count=10)

    def test_plot_confirms_plot_by_good_gps(self):
        """Asserts a target can be confirmed."""
        plot = mommy.make_recipe('plot.plot')
        self.assertFalse(Plot.objects.get(pk=plot.pk).confirmed)
        plot.gps_confirmed_latitude = fake.confirmed_latitude()
        plot.gps_confirmed_longitude = fake.confirmed_longitude()
        plot.save()
        self.assertTrue(Plot.objects.get(pk=plot.pk).confirmed)

    def test_plot_raises_on_bad_gps(self):
        """Asserts a target can be confirmed."""
        plot = mommy.make_recipe(
            'plot.plot',
            gps_target_lat=fake.target_latitude,
            gps_target_lon=fake.target_longitude)
        self.assertFalse(Plot.objects.get(pk=plot.pk).confirmed)
        plot.gps_confirmed_latitude = fake.latitude()
        plot.gps_confirmed_longitude = fake.longitude()
        self.assertRaises(MapperError, plot.save)

    def test_plot_save_on_change(self):
        """Allows change of residential_habitable plot even though no log entry or members have been added yet."""
        plot = mommy.make_recipe('plot.plot', status=INACCESSIBLE)
        plot.status = RESIDENTIAL_HABITABLE
        plot.save()
        self.assertEqual(Plot.objects.get(pk=plot.pk).status, RESIDENTIAL_HABITABLE)

    def test_validate_confirmed_plot_changed_to_inaccessible(self):
        plot = self.make_confirmed_plot()
        plot_log_entry = self.make_plot_log_entry(plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertFalse(plot.accessible)
        self.assertIsNone(plot.gps_confirmed_latitude)
        self.assertIsNone(plot.gps_confirmed_longitude)
        self.assertFalse(plot.confirmed)
