from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_sync.models import OutgoingTransaction
from edc_sync.tests import SyncTestHelper
from survey.tests import SurveyTestHelper

from ..sync_models import sync_models
from .plot_test_helper import PlotTestHelper


@tag('natural_keys')
class TestNaturalKey(TestCase):

    plot_helper = PlotTestHelper()
    survey_helper = SurveyTestHelper()
    sync_helper = SyncTestHelper()

    def setUp(self):
        self.survey_helper.load_test_surveys()

    def test_natural_key_attrs(self):
        self.sync_helper.sync_test_natural_key_attr('plot')

    def test_get_by_natural_key_attr(self):
        self.sync_helper.sync_test_get_by_natural_key_attr('plot')

    def test_sync_test_natural_keys(self):
        self.plot_helper.make_confirmed_plot(household_count=1)
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
        self.sync_helper.sync_test_natural_keys(
            completed_model_objs, verbose=verbose)
