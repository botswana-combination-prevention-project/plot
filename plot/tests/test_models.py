from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.test.utils import override_settings
from model_mommy import mommy

from edc_device.constants import CLIENT, CENTRAL_SERVER
from edc_map.exceptions import MapperError
from edc_map.validators import is_valid_map_area
from edc_sync.models import OutgoingTransaction
from edc_sync.test_mixins import SyncTestSerializerMixin

from household.models import Household

from ..constants import (
    RESIDENTIAL_HABITABLE, INACCESSIBLE, ACCESSIBLE, TWENTY_PERCENT)
from ..exceptions import (
    PlotIdentifierError, MaxHouseholdsExceededError,
    PlotEnrollmentError, PlotCreateError,
    CreateHouseholdError, PlotConfirmationError)
from ..models import Plot, PlotLog, PlotLogEntry
from ..mommy_recipes import fake, get_utcnow
from ..sync_models import sync_models

from .mixins import PlotMixin


class TestPlotCreatePermissions(PlotMixin, TestCase):
    """Assert permissions / roles that can create plots.
    """

    def setUp(self):
        super().setUp()
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)

    @override_settings(DEVICE_ID='99')
    def test_create_plot_server(self):
        """Asserts a plot may be created by a server.
        """
        django_apps.app_configs['edc_device'].ready(verbose_messaging=False)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CENTRAL_SERVER)
        try:
            self.make_plot()
        except PlotIdentifierError:
            self.fail('PlotIdentifierError unexpectedly raised')

    @override_settings(DEVICE_ID='00')
    def test_create_plot_client(self):
        django_apps.app_configs['edc_device'].ready(
            verbose_messaging=False)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CLIENT)
        try:
            self.make_plot()
        except PlotIdentifierError as e:
            self.fail('PlotIdentifierError unexpectedly raised. '
                      'Got {}'.format(e))

    @override_settings(DEVICE_ID='99')
    def test_create_plot_enrolled_cannot_unconfirm(self):
        """Assert cannot unconfirm an enrolled plot.
        """
        django_apps.app_configs['edc_device'].ready(
            verbose_messaging=False)
        plot = self.make_confirmed_plot()
        django_apps.app_configs['edc_device'].device_id = '00'
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.assertEqual(edc_device_app_config.role, CLIENT)
        plot.enrolled = True
        plot.enrolled_datetime = get_utcnow()
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        plot.gps_confirmed_latitude = None
        plot.gps_confirmed_longitude = None
        self.assertRaises(PlotEnrollmentError, plot.save)


class TestPlotCreateCommunity(TestCase):

    def test_community_validator(self):
        self.assertRaises(
            ValidationError, is_valid_map_area, 'wrong_community')
        try:
            is_valid_map_area('test_community')
        except ValidationError:
            self.fail('ValidationError unexpectedly raised')


@override_settings(DEVICE_ID='99')
class TestPlot(PlotMixin, TestCase):

    def setUp(self):
        super().setUp()
        django_apps.app_configs['edc_device'].ready(
            verbose_messaging=False)

    def test_datetime(self):
        self.assertIsNotNone(self.get_utcnow())

    def test_plot_confirmation(self):
        """Assert that confirming a plot with coorect coordinates allows
        a plot to be confirmed=True.
        """
        plot_options = {'gps_target_lat': -25.330234,
                        'gps_target_lon': 25.556882, 'map_area': 'test_community', 'ess': True}
        plot = self.make_plot(**plot_options)
        self.assertFalse(plot.confirmed)
        options = {}
        options['report_datetime'] = options.get(
            'report_datetime', self.get_utcnow())
        self.add_plot_log_entry(
            plot=plot, log_status=ACCESSIBLE,
            **options)
        plot.household_count = 1
        plot.status = RESIDENTIAL_HABITABLE
        plot.gps_confirmed_latitude = -25.330259
        plot.gps_confirmed_longitude = 25.556885
        plot.time_of_day = 'mornings'
        plot.time_of_week = 'weekdays'
        plot.save()
        self.assertTrue(plot.confirmed)

    def test_plot_creates_household(self):
        """Assert creating a plot with a household count creates
        that many households.
        """
        plot = self.make_confirmed_plot(household_count=1)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 1)
        plot = self.make_confirmed_plot(household_count=2)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 2)
        plot = self.make_confirmed_plot(household_count=3)
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

    def test_plot_add_subtract_household(self):
        """Assert change number of households will delete and recreate.
        """
        plot = self.make_confirmed_plot(household_count=3)
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
        self.assertRaises(
            MaxHouseholdsExceededError,
            self.make_confirmed_plot, household_count=10)

    def test_plot_confirms_plot_by_good_gps(self):
        """Asserts a target can be confirmed.
        """
        plot = mommy.make_recipe('plot.plot')
        self.assertFalse(Plot.objects.get(pk=plot.pk).confirmed)
        plot.gps_confirmed_latitude = fake.confirmed_latitude()
        plot.gps_confirmed_longitude = fake.confirmed_longitude()
        plot.save()
        self.assertTrue(Plot.objects.get(pk=plot.pk).confirmed)

    def test_plot_raises_on_bad_gps(self):
        """Asserts a target can be confirmed.
        """
        plot = mommy.make_recipe(
            'plot.plot',
            gps_target_lat=fake.target_latitude,
            gps_target_lon=fake.target_longitude)
        self.assertFalse(Plot.objects.get(pk=plot.pk).confirmed)
        plot.gps_confirmed_latitude = fake.latitude()
        plot.gps_confirmed_longitude = fake.longitude()
        self.assertRaises(MapperError, plot.save)

    def test_plot_save_on_change(self):
        """Allows change of residential_habitable plot even though no
        log entry or members have been added yet.
        """
        plot = mommy.make_recipe('plot.plot', status=INACCESSIBLE)
        plot.status = RESIDENTIAL_HABITABLE
        plot.save()
        self.assertEqual(
            Plot.objects.get(pk=plot.pk).status, RESIDENTIAL_HABITABLE)

    def test_validate_confirmed_plot_changed_to_inaccessible(self):
        plot = self.make_confirmed_plot()
        plot_log_entry = self.add_plot_log_entry(
            plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertFalse(plot.accessible)
        self.assertIsNone(plot.gps_confirmed_latitude)
        self.assertIsNone(plot.gps_confirmed_longitude)
        self.assertFalse(plot.confirmed)

    def test_access_attempts(self):
        plot = self.make_confirmed_plot()
        self.add_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(plot.access_attempts, 1)
        self.add_plot_log_entry(plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot.pk)
        self.assertEqual(plot.access_attempts, 2)

    def test_accessible_can_create_households(self):
        plot = self.make_plot()
        self.add_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot = self.confirm_plot(plot)
        plot.household_count = 3
        plot.save()
        self.assertEqual(Household.objects.filter(plot=plot).count(), 3)

    def test_inaccessible_cannot_have_eligibles(self):
        plot = self.make_plot()
        self.add_plot_log_entry(plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot.pk)
        plot.eligible_members = 5
        self.assertRaises(CreateHouseholdError, plot.save)

    def test_inaccessible_plot_can_be_confirmed(self):
        plot = self.make_plot()
        self.add_plot_log_entry(plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot.pk)
        try:
            self.confirm_plot(plot)
        except PlotConfirmationError:
            self.fail('PlotConfirmationError unexpectedly raised')

    def test_create_plot1(self):
        """Assert rss is false if not a selected plot.
        """
        plot = self.make_plot(selected=None)
        self.assertFalse(plot.rss)

    def test_create_plot2(self):
        """Assert rss true if a selected plot.
        """
        plot = self.make_plot(selected=TWENTY_PERCENT)
        self.assertTrue(plot.rss)

    def test_create_plot3(self):
        """Assert can create plot for use by HTC outside of RSS.
        """
        plot = self.make_plot(htc=True, selected=None)
        self.assertTrue(plot.htc)

    def test_create_plot4(self):
        """Assert cannot create plot for use by HTC and ESS.
        """
        self.assertRaises(
            PlotEnrollmentError,
            self.make_plot, htc=True, selected=None, ess=True)

    def test_create_plot5(self):
        """Asserts cannot allocate new plot to both RSS and HTC."""
        self.assertRaises(
            PlotCreateError,
            self.make_plot, htc=True, selected=TWENTY_PERCENT)

    def test_create_plot6(self):
        """Assert can set ESS true regardless."""
        plot = self.make_plot(ess=True)
        self.assertTrue(plot.ess)

    def test_does_not_create_log_for_htc_if_not_ess(self):
        plot = self.make_plot(htc=True, selected=None)
        self.assertTrue(plot.htc)
        try:
            self.add_plot_log_entry(plot=plot)
            self.fail('PlotLog.DoesNotExist unexpcedtedly not raised')
        except PlotLog.DoesNotExist:
            pass

    def test_cannot_confirm_without_log(self):
        plot = self.make_plot()
        self.confirm_plot(plot)

    def test_cannot_create_plot_enrolled_without_date(self):
        """Assert cannot update enrolled without enrollment date.
        """
        plot = self.make_confirmed_plot()
        plot.enrolled = True
        self.assertRaises(PlotEnrollmentError, plot.save)

    def test_accessible_and_confirmed_can_be_inaccessible(self):
        plot = self.make_plot()
        self.add_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot = self.confirm_plot(plot)
        plot.household_count = 3
        plot.save()
        try:
            self.add_plot_log_entry(plot=plot, log_status=INACCESSIBLE)
        except (CreateHouseholdError, PlotConfirmationError) as e:
            self.fail('Exception unexpectedly raised. Got {}'.format(str(e)))

    def test_accessible_and_confirmed_can_be_inaccessible_if_enrolled(self):
        plot = self.make_plot()
        self.add_plot_log_entry(plot=plot, log_status=ACCESSIBLE)
        plot = self.confirm_plot(plot)
        plot.household_count = 3
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        plot.enrolled = True
        plot.enrolled_datetime = get_utcnow()
        plot.save()
        plot = Plot.objects.get(pk=plot.pk)
        self.assertRaises(
            PlotEnrollmentError,
            self.add_plot_log_entry, plot=plot, log_status=INACCESSIBLE)

    def test_log_entry_sets_accessible_attr(self):
        plot = self.make_confirmed_plot()
        plot_log_entry = self.add_plot_log_entry(
            plot=plot, log_status=INACCESSIBLE)
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertFalse(plot.accessible)
        plot_log_entry = self.add_plot_log_entry(
            plot=plot, log_status=ACCESSIBLE)
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertTrue(plot.accessible)

    def test_plot_resets_accessible_attr_if_no_logentry(self):
        plot = self.make_confirmed_plot()
        plot_log_entry = PlotLogEntry.objects.get(plot_log__plot=plot)
        plot_log_entry.log_status = INACCESSIBLE
        plot_log_entry.save()
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertFalse(plot.accessible)
        plot_log_entry.delete()
        plot = Plot.objects.get(pk=plot_log_entry.plot_log.plot.pk)
        self.assertTrue(plot.accessible)


class TestNaturalKey(SyncTestSerializerMixin, PlotMixin, TestCase):

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('plot')

    def test_get_by_natural_key_attr(self):
        self.sync_test_get_by_natural_key_attr('plot')

    def test_sync_test_natural_keys(self):
        self.make_confirmed_plot(household_count=1)
        verbose = False
        model_objs = []
        completed_model_objs = {}
        completed_model_lower = []
        for outgoing_transaction in OutgoingTransaction.objects.all():
            if outgoing_transaction.tx_name in sync_models:
                model_cls = django_apps.get_app_config('plot').get_model(
                    outgoing_transaction.tx_name.split('.')[1])
                obj = model_cls.objects.get(pk=outgoing_transaction.tx_pk)
                if outgoing_transaction.tx_name in completed_model_lower:
                    continue
                model_objs.append(obj)
                completed_model_lower.append(outgoing_transaction.tx_name)
        completed_model_objs.update({'plot': model_objs})
        self.sync_test_natural_keys(completed_model_objs, verbose=verbose)
