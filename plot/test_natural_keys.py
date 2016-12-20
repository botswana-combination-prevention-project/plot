from django.test import TestCase

from edc_sync.test_mixins import SyncTestSerializerMixin

from .test_mixins import PlotMixin


class TestNaturalKey(SyncTestSerializerMixin, PlotMixin, TestCase):

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('plot')

    def test_get_by_natural_key_attr(self):
        self.sync_test_get_by_natural_key_attr('plot')
