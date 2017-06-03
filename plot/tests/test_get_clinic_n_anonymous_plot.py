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
        get_clinic_n_anonymous_plot(
            plot_identifier=plot_identifier, plot_type=plot_type)
        self.assertEqual(Plot.objects.all().count(), 1)
