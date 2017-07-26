from django.apps import apps as django_apps

from edc_model_wrapper.wrappers import ModelWrapper


class PlotModelWrapper(ModelWrapper):

    model = 'plot.plot'
    next_url_name = django_apps.get_app_config(
        'plot_dashboard').listboard_url_name
    next_url_attrs = ['plot_identifier']
