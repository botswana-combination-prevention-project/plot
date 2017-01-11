from django.apps import apps as django_apps

from edc_dashboard.wrappers import ModelWrapper, ModelWithLogWrapper


class PlotModelWrapper(ModelWrapper):

    admin_site_name = django_apps.get_app_config('plot').admin_site_name
    url_namespace = django_apps.get_app_config('plot').url_namespace
    next_url_name = django_apps.get_app_config('plot').listboard_url_name


class PlotWrapper(PlotModelWrapper):

    model_name = 'plot.plot'
    extra_querystring_attrs = {}
    next_url_attrs = {'plot.plot': ['plot_identifier']}
    url_instance_attrs = ['plot_identifier']


class PlotLogEntryWrapper(PlotModelWrapper):

    model_name = 'plot.plotlogentry'
    extra_querystring_attrs = {'plot.plotlogentry': ['plot_log']}
    next_url_attrs = {'plot.plotlogentry': ['plot_identifier']}
    url_instance_attrs = ['plot_log', 'plot_identifier']

    @property
    def plot_identifier(self):
        return self._original_object.plot_log.plot.plot_identifier


class PlotWithLogEntryWrapper(ModelWithLogWrapper):

    model_wrapper_class = PlotWrapper
    log_entry_model_wrapper_class = PlotLogEntryWrapper

    @property
    def plot_identifier(self):
        return self._original_object.plot_identifier
