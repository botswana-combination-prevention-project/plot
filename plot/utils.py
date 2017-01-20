from django.apps import apps as django_apps

from edc_base.utils import get_utcnow

from .constants import RESIDENTIAL_HABITABLE
from .models import Plot


def get_anonymous_plot():
    plot_identifier = django_apps.get_app_config('plot').anonymous_plot_identifier
    try:
        plot = Plot.objects.get(plot_identifier=plot_identifier)
    except Plot.DoesNotExist:
        lat = -30.2671500
        lon = 97.7430600
        plot = Plot.objects.create(
            plot_identifier=plot_identifier,
            report_datetime=get_utcnow(),
            map_area='austin',
            description='anonymous',
            comment='anonymous',
            status=RESIDENTIAL_HABITABLE,
            household_count=1,
            eligible_members=1,
            selected=None,
            gps_target_lat=lat,
            gps_target_lon=lon,
            gps_confirmed_latitude=lat,
            gps_confirmed_longitude=lon,
            ess=True,
            rss=False,
            htc=False)
    return plot
