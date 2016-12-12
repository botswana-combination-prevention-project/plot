from django.test import TestCase, tag

from django.test.utils import override_settings
from django.core.exceptions import ValidationError

from .helper import PlotHelperError
from .models import Plot
from .validators import is_valid_community


@tag('review')
class TestPlot(TestCase):

    @override_settings(DEVICE_ID='99')
    def test_create_plot_server(self):
        self.assertRaises(PlotHelperError, Plot.objects.create)

    @override_settings(DEVICE_ID='00')
    def test_create_plot_client(self):
        plot = Plot.objects.create()
        self.assertIsNotNone(plot.plot_identifier)

    def test_community_validator(self):
        self.assertRaises(ValidationError, is_valid_community, 'erik')
        try:
            is_valid_community('digawana')
        except ValidationError:
            self.fail('ValidationError unexpectedly raised')
