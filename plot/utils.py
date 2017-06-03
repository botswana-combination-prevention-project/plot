from django.apps import apps as django_apps

from edc_base.utils import get_utcnow
from edc_map.site_mappers import site_mappers

from .constants import RESIDENTIAL_HABITABLE
from .models import Plot


def get_clinic_n_anonymous_plot(plot_identifier=None, plot_type=None, **kwargs):
    """Return a clinic plot or an anonymous plot.
    """
    device_id = django_apps.get_app_config(
        'edc_device').device_id
    try:
        plot = Plot.objects.get(plot_identifier=plot_identifier)
    except Plot.DoesNotExist:
        lat = (site_mappers.current_mapper.center_lat
               + float('.000000{}'.format(device_id)))
        lon = (site_mappers.current_mapper.center_lon
               + float('.000000{}'.format(device_id)))
        plot = Plot.objects.create(
            plot_identifier=plot_identifier,
            report_datetime=get_utcnow(),
            map_area=site_mappers.current_map_area,
            description=plot_type,
            comment=plot_type,
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
