import arrow

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.views.generic import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_search.forms import SearchForm
from edc_search.view_mixins import SearchViewMixin

from .models import Plot, PlotLog, PlotLogEntry

app_config = django_apps.get_app_config('plot')


class SearchPlotForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse('plot:list_url')


class Result:
    def __init__(self, plot):
        self.plot = plot
        self.plot.community_name = ' '.join(self.plot.map_area.split('_'))
        self.plot_log = PlotLog.objects.get(plot=plot)
        try:
            self.plot_log_entries = PlotLogEntry.objects.filter(plot_log__plot=plot)
        except PlotLogEntry.DoesNotExist:
            self.plot_log_entries = None
        try:
            self.plot_log_entry_today = PlotLogEntry.objects.get(
                plot_log__plot=plot,
                report_datetime__year=arrow.utcnow().year,
                report_datetime__month=arrow.utcnow().month,
                report_datetime__day=arrow.utcnow().day)
        except PlotLogEntry.DoesNotExist:
            self.plot_log_entry_today = None
        self.plot_log_entry_link_html_class = "disabled" if plot.confirmed else "active"


class PlotsView(EdcBaseViewMixin, TemplateView, SearchViewMixin, FormView):

    form_class = SearchPlotForm
    template_name = app_config.list_template_name
    paginate_by = 10
    search_url_name = 'plot:list_url'
    search_model = Plot

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def search_options(self, search_term, **kwargs):
        q = (
            Q(plot_identifier__icontains=search_term) |
            Q(user_created__iexact=search_term) |
            Q(user_modified__iexact=search_term))
        options = {}
        return q, options

    def queryset_wrapper(self, qs):
        results = []
        for obj in qs:
            results.append(Result(obj))
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plot_results = Plot.objects.all().order_by('-created')
        context.update(
            search_url_name=self.search_url_name,
            navbar_selected='plot',
            results=self.paginate(plot_results))
        return context
