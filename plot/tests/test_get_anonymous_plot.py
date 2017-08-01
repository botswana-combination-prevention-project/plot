from django.apps import apps as django_apps
from django.test import TestCase

from edc_map.site_mappers import site_mappers
from survey.tests import SurveyTestHelper

from ..models import Plot
from ..utils import get_anonymous_plot
from .mappers import TestPlotMapper


class TestCreateAnonymousPlot(TestCase):
    """Assert permissions / roles that can create plots.
    """
    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()
        django_apps.app_configs['edc_device'].device_id = '99'
        site_mappers.registry = {}
        site_mappers.loaded = False
        site_mappers.register(TestPlotMapper)

    def test_create_anonymous_plot(self):
        """Test creating a clinic plot.
        """
        get_anonymous_plot()
        self.assertEqual(Plot.objects.all().count(), 1)
