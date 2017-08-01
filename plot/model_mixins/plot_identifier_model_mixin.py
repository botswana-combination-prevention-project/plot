# coding=utf-8

from django.db import models

from edc_identifier.research_identifier import ResearchIdentifier
from edc_map.site_mappers import site_mappers


class PlotIdentifierError(Exception):
    pass


class PlotIdentifier(ResearchIdentifier):
    def __init__(self, map_code=None, **kwargs):
        self.map_code = map_code
        super().__init__(**kwargs)

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

    def save(self, *args, **kwargs):
        """Allocates a plot identifier to a new instance if
        permissions allow.
        """
        if not self.id and not self.plot_identifier:
            self.plot_identifier = PlotIdentifier(
                map_code=site_mappers.get_mapper(
                    self.map_area).map_code,
                site_code=site_mappers.get_mapper(
                    self.map_area).map_code).identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
