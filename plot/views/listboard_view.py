from django.apps import apps as django_apps
from django.db.models import Q

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardMixin, FilteredListViewMixin
from edc_search.view_mixins import SearchViewMixin

from ..constants import RESIDENTIAL_HABITABLE
from ..models import Plot

from .wrappers import PlotWithLogEntryWrapper

app_config = django_apps.get_app_config('plot')


class ListBoardView(EdcBaseViewMixin, ListboardMixin, FilteredListViewMixin, SearchViewMixin):

    template_name = app_config.listboard_template_name
    listboard_url_name = app_config.listboard_url_name

    search_model = Plot
    search_model_wrapper_class = PlotWithLogEntryWrapper
    search_queryset_ordering = '-modified'

    filter_model = Plot
    filtered_model_wrapper_class = PlotWithLogEntryWrapper
    filtered_queryset_ordering = '-modified'
    url_lookup_parameters = ['id', 'plot_identifier']

    def search_options_for_date(self, search_term, **kwargs):
        """Adds report_datetime to search by date."""
        q, options = super().search_options_for_date(search_term, **kwargs)
        q = q | Q(report_datetime__date=search_term.date())
        return q, options

    def search_options(self, search_term, **kwargs):
        """Adds `ESS` as a special keyword in search."""
        q, options = super().search_options(search_term, **kwargs)
        if search_term.lower() == 'ess':
            options = {'ess': True}
            q = Q()
        else:
            q = q | Q(plot_identifier__icontains=search_term)
        return q, options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            navbar_selected='plot',
            RESIDENTIAL_HABITABLE=RESIDENTIAL_HABITABLE,
            household_listboard_url_name=django_apps.get_app_config('household').listboard_url_name,
            map_url_name='plot:map_url')
        return context
