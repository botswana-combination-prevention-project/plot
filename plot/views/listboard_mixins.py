from django.apps import apps as django_apps
from django.db.models import Q

from edc_dashboard.view_mixins import (
    FilteredListViewMixin as BaseFilteredListViewMixin,
    AppConfigViewMixin as BaseAppConfigViewMixin)
from edc_search.view_mixins import SearchViewMixin as BaseSearchViewMixin

from ..models import Plot

from .wrappers import PlotWithLogEntryModelWrapper


class AppConfigViewMixin(BaseAppConfigViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            map_url_name=django_apps.get_app_config('plot').map_url_name,
        )
        return context


class SearchViewMixin(BaseSearchViewMixin):

    search_model = Plot
    search_model_wrapper_class = PlotWithLogEntryModelWrapper
    search_queryset_ordering = '-modified'

    def search_options_for_date(self, search_term, **kwargs):
        """Adds report_datetime to search by date.
        """
        q, options = super().search_options_for_date(search_term, **kwargs)
        q = q | Q(report_datetime__date=search_term.date())
        return q, options

    def search_options(self, search_term, **kwargs):
        """Adds `ESS` as a special keyword in search.
        """
        q, options = super().search_options(search_term, **kwargs)
        if search_term.lower() == 'ess':
            options = {'ess': True}
            q = Q()
        else:
            q = q | Q(plot_identifier__icontains=search_term)
        return q, options


class FilteredListViewMixin(BaseFilteredListViewMixin):

    filter_model = Plot
    filtered_model_wrapper_class = PlotWithLogEntryModelWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = [
        ('id', 'id'),
        ('plot_identifier', 'plot_identifier')]
