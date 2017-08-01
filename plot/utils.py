from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_base.utils import get_utcnow
from edc_map.site_mappers import site_mappers

from .constants import RESIDENTIAL_HABITABLE


def get_anonymous_plot(plot_model=None, **kwargs):
    """Return a clinic plot or an anonymous plot.
    """
    if not plot_model:
        plot_model = 'plot.plot'
    plot_model_cls = django_apps.get_model(plot_model)
    device_id = django_apps.get_app_config(
        'edc_device').device_id
    plot_identifier = django_apps.get_app_config(
        'plot').anonymous_plot_identifier
    try:
        plot = plot_model_cls.objects.get(plot_identifier=plot_identifier)
    except ObjectDoesNotExist:
        lat = (site_mappers.current_mapper.center_lat
               + float('.000000{}'.format(device_id)))
        lon = (site_mappers.current_mapper.center_lon
               + float('.000000{}'.format(device_id)))
        plot = plot_model_cls.objects.create(
            plot_identifier=plot_identifier,
            report_datetime=get_utcnow(),
            map_area=site_mappers.current_map_area,
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
