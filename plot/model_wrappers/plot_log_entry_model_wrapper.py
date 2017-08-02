from django.apps import apps as django_apps

from edc_model_wrapper.wrappers import ModelWrapper


class PlotLogEntryModelWrapper(ModelWrapper):

    model = 'plot.plotlogentry'
    next_url_name = django_apps.get_app_config(
        'plot_dashboard').listboard_url_name
    url_namespace = 'plot_dashboard'
    next_url_attrs = ['plot_identifier']
    querystring_attrs = ['plot_log']

    @property
    def plot_identifier(self):
        return self.object.plot_log.plot.plot_identifier

    @property
    def plot_log(self):
        return self.object.plot_log.id
