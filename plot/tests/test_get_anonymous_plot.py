from django.test import TestCase

from ..models import Plot
from ..utils import get_anonymous_plot


class TestCreateAnonymousPlot(TestCase):
    """Assert permissions / roles that can create plots.
    """

    def setUp(self):
        pass

    def test_create_anonymous_plot(self):
        """Test creating a clinic plot.
        """
        get_anonymous_plot()
        self.assertEqual(Plot.objects.all().count(), 1)
