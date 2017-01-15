from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardViewMixin

from ..constants import RESIDENTIAL_HABITABLE

from .listboard_mixins import PlotSearchViewMixin, PlotFilteredListViewMixin, PlotAppConfigViewMixin


class ListBoardView(EdcBaseViewMixin, ListboardViewMixin, PlotAppConfigViewMixin,
                    PlotFilteredListViewMixin, PlotSearchViewMixin, TemplateView, FormView):

    app_config_name = 'plot'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            RESIDENTIAL_HABITABLE=RESIDENTIAL_HABITABLE)
        return context
