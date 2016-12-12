from django.apps.config import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'bcpp_plot'
