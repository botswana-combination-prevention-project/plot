# coding=utf-8

from django.apps import apps as django_apps
from django.db import models

from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.site_mappers import site_mappers


class PlotIdentifierError(Exception):
    pass


class PlotIdentifier(ResearchIdentifier):

    template = '{map_code}{sequence}'
    label = 'plot_identifier'


class PlotIdentifierModelMixin(models.Model):
    """Mixin to allocate a plot identifier.
    """

    plot_identifier = models.CharField(
        verbose_name='Plot Identifier',
        max_length=25,
        unique=True,
        editable=False)

    def common_clean(self):
        """Block a device without permissions from allocating a
        plot identifier to a new instance.
        """
        if not self.id and not self.plot_identifier:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = (
                edc_device_app_config.device_permissions.get(
                    self._meta.label_lower))
            if not device_permissions.may_add(edc_device_app_config.role):
                raise PlotIdentifierError(
                    'Blocking attempt to create plot identifier. '
                    f'Got device \'{edc_device_app_config.role}\'.')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [PlotIdentifierError]

    def save(self, *args, **kwargs):
        """Allocates a plot identifier to a new instance if
        permissions allow.
        """
        if not self.id and not self.plot_identifier:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            device_permissions = (
                edc_device_app_config.device_permissions.get(
                    self._meta.label_lower))
            if device_permissions and device_permissions.may_add(edc_device_app_config.role):
                if not self.id:
                    self.plot_identifier = PlotIdentifier(
                        map_code=site_mappers.get_mapper(
                            self.map_area).map_code,
                        study_site=site_mappers.get_mapper(
                            self.map_area).map_code).identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
