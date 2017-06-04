import re

from django.apps import apps as django_apps
from django.test import TestCase

from ..models import Plot
from ..utils import get_clinic_n_anonymous_plot


class TestCreateClinicAnonymousPlot(TestCase):
    """Assert permissions / roles that can create plots.
    """

    def setUp(self):
        pass

    def test_create_clinic_plot(self):
        """Test creating a clinic plot.
        """
        plot_identifier = django_apps.get_app_config(
            'plot').clinic_plot_identifiers[0]
        plot_type = 'clinic'
        plot = get_clinic_n_anonymous_plot(
            plot_identifier=plot_identifier, plot_type=plot_type)
        pattern = re.compile("[0-9]{2}[0000-00]")
        self.assertTrue(pattern.match(plot.plot_identifier))
        self.assertEqual(Plot.objects.all().count(), 1)

    def test_create_anonymous_plot(self):
        """Test creating a clinic plot.
        """
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        plot_type = 'anonymous'
        plot = get_clinic_n_anonymous_plot(
            plot_identifier=plot_identifier, plot_type=plot_type)
        pattern = re.compile("[0-9]{2}[1-9]{2}[00-00]")
        self.assertTrue(pattern.match(plot.plot_identifier))
        self.assertEqual(Plot.objects.all().count(), 1)

    def test_create_both_anonymous_n_clinic_plot(self):
        """Test creating a clinic plot.
        """
        anonymous_plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        clinic_plot_identifier = django_apps.get_app_config(
            'plot').clinic_plot_identifiers[0]

        anonymous_plot_type = 'anonymous'
        clinic_plot_type = 'clinic'

        get_clinic_n_anonymous_plot(
            plot_identifier=anonymous_plot_identifier, plot_type=anonymous_plot_type)
        get_clinic_n_anonymous_plot(
            plot_identifier=clinic_plot_identifier, plot_type=clinic_plot_type)

        self.assertEqual(Plot.objects.all().count(), 2)
