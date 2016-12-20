from django.test import TestCase, tag
from django.apps import apps as django_apps

from edc_sync.test_mixins import SyncTestSerializerMixin

from edc_sync.models import OutgoingTransaction

from ..sync_models import sync_models

from .test_mixins import HouseholdMixin


class TestNaturalKey(SyncTestSerializerMixin, HouseholdMixin, TestCase):

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('plot')

    def test_get_by_natural_key_attr(self):
        self.sync_test_get_by_natural_key_attr('plot')
