from django.test import TestCase, tag

from edc_sync.test_mixins import SyncTestSerializerMixin
from survey.tests import SurveyTestHelper

# from ..sync_models import sync_models


@tag('natural_keys')
class TestNaturalKey(SyncTestSerializerMixin, TestCase):

    survey_helper = SurveyTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_natural_key_attrs(self):
        self.sync_test_natural_key_attr('plot')

    def test_get_by_natural_key_attr(self):
        self.sync_test_get_by_natural_key_attr('plot')
