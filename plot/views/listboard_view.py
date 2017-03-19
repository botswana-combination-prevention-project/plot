import socket

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_map.models import InnerContainer


from ..constants import RESIDENTIAL_HABITABLE
from ..models import Plot

from .wrappers import PlotWithLogEntryModelWrapper


class ListBoardView(AppConfigViewMixin, EdcBaseViewMixin, BaseListboardView):

    app_config_name = 'plot'
    navbar_item_selected = 'plot'
    model = Plot
    model_wrapper_class = PlotWithLogEntryModelWrapper

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            RESIDENTIAL_HABITABLE=RESIDENTIAL_HABITABLE,
            map_url_name=django_apps.get_app_config('plot').map_url_name,
        )
        return context

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        options = super().get_queryset_exclude_options(
            request, *args, **kwargs)
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        options.update({'plot_identifier': plot_identifier})
        return options

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        map_area = settings.CURRENT_MAP_AREA
        options.update(
            {'map_area': map_area})
        plot_identifier = kwargs.get('plot_identifier')
        device_id = socket.gethostname()[-2:]
        if plot_identifier:
            options.update(
                {'plot_identifier': plot_identifier})
        plot_identifier_list = []
        try:
            plot_identifier_list = InnerContainer.objects.get(
                device_id=device_id).identifier_labels
        except InnerContainer.DoesNotExist:
            plot_identifier_list = []
        if plot_identifier_list:
            options.update(
                {'plot_identifier__in': plot_identifier_list})
        return options
