from django.test import TestCase, tag

from .models import Plot


@tag('review')
class TestPlot(TestCase):

    def test_model(self):
        plot = Plot()
        plot.save()
