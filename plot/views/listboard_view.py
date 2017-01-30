from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardViewMixin

from ..constants import RESIDENTIAL_HABITABLE

from .listboard_mixins import (
    SearchViewMixin, FilteredListViewMixin, AppConfigViewMixin)


class ListBoardView(FilteredListViewMixin, SearchViewMixin,
                    AppConfigViewMixin, ListboardViewMixin,
                    EdcBaseViewMixin, TemplateView, FormView):

    app_config_name = 'plot'
    navbar_item_selected = 'plot'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            RESIDENTIAL_HABITABLE=RESIDENTIAL_HABITABLE)
        return context

    @property
    def filtered_queryset(self):
        qs = super().filtered_queryset
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        return qs.exclude(
            household__plot__plot_identifier=plot_identifier).order_by(
                self.filtered_queryset_ordering)

    def search_queryset(self, search_term, **kwargs):
        qs = super().search_queryset(search_term, **kwargs)
        plot_identifier = django_apps.get_app_config(
            'plot').anonymous_plot_identifier
        return qs.exclude(
            household__plot__plot_identifier=plot_identifier).order_by(
                self.filtered_queryset_ordering)
