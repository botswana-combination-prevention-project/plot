from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP

from edc_device.constants import CLIENT, SERVER
from edc_map.models import InnerContainer
from edc_map.site_mappers import site_mappers


class PlotQuerysetViewMixin:

    plot_queryset_lookups = []

    @property
    def plot_lookup_prefix(self):
        plot_lookup_prefix = LOOKUP_SEP.join(self.plot_queryset_lookups)
        return '{}__'.format(plot_lookup_prefix) if plot_lookup_prefix else ''

    @property
    def plot_identifiers(self):
        """Returns a list of plot identifiers allocated to this device.
        """
        edc_device_app_config = django_apps.get_app_config('edc_device')
        device_id = edc_device_app_config.device_id
        plot_identifiers = []
        try:
            plot_identifiers = InnerContainer.objects.get(
                device_id=device_id,
                map_area=site_mappers.current_map_area).identifier_labels
        except InnerContainer.DoesNotExist:
            pass
        return plot_identifiers

    def add_device_filter_options(self, options=None, **kwargs):
        """Updates the filter options to limit the plots returned
        to those allocated to this client device_id.
        """
        if kwargs.get('plot_identifier'):
            options.update(
                {'{}plot_identifier'.format(self.plot_lookup_prefix): kwargs.get('plot_identifier')})
        elif self.plot_identifiers:
            options.update(
                {'{}plot_identifier__in'.format(self.plot_lookup_prefix): self.plot_identifiers})
        return options

    def add_map_area_filter_options(self, options=None, **kwargs):
        """Updates the filter options to limit the plots returned
        to those in the current map_area.
        """
        map_area = site_mappers.current_map_area
        options.update(
            {'{}map_area'.format(self.plot_lookup_prefix): map_area})
        return options

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        edc_device_app_config = django_apps.get_app_config('edc_device')
        if edc_device_app_config.device_role in [SERVER, CLIENT]:
            options = self.add_map_area_filter_options(
                options=options, **kwargs)
        if edc_device_app_config.device_role == CLIENT:
            options = self.add_device_filter_options(options=options, **kwargs)
        return options

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        options = super().get_queryset_exclude_options(
            request, *args, **kwargs)
        app_config = django_apps.get_app_config('plot')
        plot_identifiers = app_config.clinic_plot_identifiers
        plot_identifiers.append(app_config.anonymous_plot_identifier)
        options.update(
            {'{}plot_identifier__in'.format(self.plot_lookup_prefix):
             plot_identifiers})
        return options
