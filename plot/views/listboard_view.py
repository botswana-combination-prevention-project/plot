from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_dashboard.view_mixins import ListboardFilterViewMixin


from ..constants import RESIDENTIAL_HABITABLE
from ..models import Plot
from ..view_mixins import PlotQuerysetViewMixin

from .listboard_filters import PlotListboardViewFilters
from .wrappers import PlotWithLogEntryModelWrapper


class ListBoardView(AppConfigViewMixin, EdcBaseViewMixin, ListboardFilterViewMixin,
                    PlotQuerysetViewMixin, BaseListboardView):

    app_config_name = 'plot'
    navbar_item_selected = 'plot'
    ordering = '-modified'
    model = Plot
    model_wrapper_class = PlotWithLogEntryModelWrapper
    listboard_view_filters = PlotListboardViewFilters()

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
