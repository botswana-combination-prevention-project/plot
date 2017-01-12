# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.apps.config import AppConfig as DjangoAppConfig
from django.utils import timezone

from edc_base.utils import get_utcnow
from edc_constants.constants import CLOSED, OPEN


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
    listboard_template_name = 'plot/listboard.html'
    listboard_url_name = 'plot:listboard_url'
    url_namespace = 'plot'
    admin_site_name = 'plot_admin'
    enrollment = Enrollment(
        timezone.now() - relativedelta(years=1),
        timezone.now() + relativedelta(years=1))
    max_households = 9
    special_locations = ['clinic', 'mobile']
    add_plot_map_areas = ['test_community']
    map_url_name = 'plot:map_url'

    def ready(self):
        from plot.signals import plot_creates_households_on_post_save, update_plot_on_post_save

    def excluded_plot(self, obj):
        """Returns True if the plot is excluded from being surveyed.

        If True, no further data will be added, e.g. no plot log, etc. See signals"""
        excluded_plot = False
        if obj.htc and not obj.ess:
            excluded_plot = True
        return excluded_plot

    def allow_add_plot(self, map_area):
        return True if map_area in self.add_plot_map_areas else False
