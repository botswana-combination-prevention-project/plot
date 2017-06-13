from django.apps import apps as django_apps

from edc_model_wrapper.wrappers import ModelWrapper, ModelWithLogWrapper


class PlotModelWrapper(ModelWrapper):

    model_name = 'plot.plot'
    next_url_name = django_apps.get_app_config('plot').listboard_url_name
    next_url_attrs = ['plot_identifier']


class PlotLogEntryModelWrapper(ModelWrapper):

    model_name = 'plot.plotlogentry'
    next_url_name = django_apps.get_app_config('plot').listboard_url_name
    next_url_attrs = ['plot_identifier']
    querystring_attrs = ['plot_log']

    @property
    def plot_identifier(self):
        return self.object.plot_log.plot.plot_identifier


class PlotWithLogEntryModelWrapper(ModelWithLogWrapper):

    model_name = 'plot.plot'
    model_wrapper_class = PlotModelWrapper
    log_entry_model_wrapper_class = PlotLogEntryModelWrapper
    next_url_name = django_apps.get_app_config('plot').listboard_url_name

    @property
    def plot_identifier(self):
        return self.object.plot_identifier
