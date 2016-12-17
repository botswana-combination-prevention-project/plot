# coding=utf-8
from django.apps.config import AppConfig as DjangoAppConfig
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import CLOSED, OPEN
from plot.constants import TWENTY_PERCENT, FIVE_PERCENT


class Enrollment:
    def __init__(self, opening_datetime, closing_datetime):
        self.opening_datetime = opening_datetime
        self.closing_datetime = closing_datetime

    @property
    def status(self, reference_datetime=None):
        reference_datetime = reference_datetime or get_utcnow()
        if self.closing_datetime < reference_datetime:
            status = CLOSED
        else:
            status = OPEN
        return status


class AppConfig(DjangoAppConfig):
    name = 'plot'
    enrollment = Enrollment(
        timezone.now() - relativedelta(years=1),
        timezone.now() + relativedelta(years=1))
    max_households = 9
    special_locations = ['clinic', 'mobile']

    def ready(self):
        from plot.signals import create_households_on_post_save, update_plot_on_post_save

    def excluded_plot(self, obj):
        if obj.htc:
            return True
        if obj.selected not in [TWENTY_PERCENT, FIVE_PERCENT]:
            return True
