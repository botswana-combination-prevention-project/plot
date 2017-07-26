# coding=utf-8

from dateutil.relativedelta import relativedelta

from django.apps import AppConfig as DjangoAppConfig, apps as django_apps
from django.utils import timezone
from django.conf import settings

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
    enrollment = Enrollment(
        timezone.now() - relativedelta(years=1),
        timezone.now() + relativedelta(years=1))
    max_households = 9
    special_locations = ['clinic', 'mobile']  # see plot.location_name
    add_plot_map_areas = ['test_community']
    supervisor_groups = ['field_supervisor']

    def ready(self):
        from plot.signals import (
            plot_creates_households_on_post_save,
            update_plot_on_post_save)

    @property
    def anonymous_plot_identifier(self):
        from edc_map.site_mappers import site_mappers
        edc_device_app_config = django_apps.get_app_config('edc_device')
        return f'{site_mappers.current_map_code}{edc_device_app_config.device_id}00-00'

    def excluded_plot(self, obj):
        """Returns True if the plot is excluded from being surveyed.

        If True, no further data will be added, e.g. no plot log, etc. See signals"""
        excluded_plot = False
        if obj.htc and not obj.ess:
            excluded_plot = True
        return excluded_plot

    @property
    def study_site_name(self):
        return None


if settings.APP_NAME == 'plot':

    from edc_map.apps import AppConfig as BaseEdcMapAppConfig

    class EdcMapAppConfig(BaseEdcMapAppConfig):
        verbose_name = 'Test Mappers'
        mapper_model = 'plot.plot'
        landmark_model = []
        verify_point_on_save = False
        zoom_levels = ['14', '15', '16', '17', '18']
        identifier_field_attr = 'plot_identifier'
        # Extra filter boolean attribute name.
        extra_filter_field_attr = 'enrolled'
