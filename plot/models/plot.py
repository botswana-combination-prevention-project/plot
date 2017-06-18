# coding=utf-8

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_device.model_mixins import DeviceModelMixin
from edc_map.exceptions import MapperError
from edc_map.model_mixins import MapperModelMixin
from edc_map.site_mappers import site_mappers
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..choices import PLOT_STATUS
from ..constants import INACCESSIBLE
from ..exceptions import PlotEnrollmentError
from ..managers import PlotManager as BasePlotManager
from ..model_mixins import PlotIdentifierModelMixin, CreateHouseholdsModelMixin
from ..model_mixins import PlotEnrollmentMixin, PlotConfirmationMixin


class PlotManager(BasePlotManager, SearchSlugManager):
    pass


class Plot(MapperModelMixin, DeviceModelMixin, PlotIdentifierModelMixin,
           PlotEnrollmentMixin, PlotConfirmationMixin,
           CreateHouseholdsModelMixin, SearchSlugModelMixin, BaseUuidModel):
    """A model created by the system and updated by the user to
    represent a Plot in the community.
    """

    def get_search_slug_fields(self):
        return ['plot_identifier', 'map_area', 'cso_number']

    report_datetime = models.DateTimeField(
        validators=[datetime_not_future],
        default=get_utcnow)

    eligible_members = models.IntegerField(
        verbose_name="Approximate number of age eligible members",
        default=0,
        null=True,
        help_text=(("Provide an approximation of the number of people "
                    "who live in this residence who are age eligible.")))

    cso_number = EncryptedCharField(
        verbose_name="CSO Number",
        blank=True,
        null=True,
        help_text=("provide the CSO number or leave BLANK."))

    time_of_week = models.CharField(
        verbose_name=(
            'Time of week when most of the eligible members will be available'),
        max_length=25,
        choices=TIME_OF_WEEK,
        blank=True,
        null=True)

    time_of_day = models.CharField(
        verbose_name=(
            'Time of day when most of the eligible members will be available'),
        max_length=25,
        choices=TIME_OF_DAY,
        blank=True,
        null=True)

    status = models.CharField(
        verbose_name='Plot status',
        max_length=35,
        choices=PLOT_STATUS,
        null=True,
        blank=False)

    description = EncryptedTextField(
        verbose_name="Description of plot/residence",
        max_length=250,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        null=True)

    accessible = models.BooleanField(
        default=True,
        editable=False)

    access_attempts = models.IntegerField(
        default=0,
        help_text=(
            'Number of attempts to access a plot to determine it\'s status.'),
        editable=False)

    objects = PlotManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {}'.format(
            self.location_name or 'undetermined', self.plot_identifier)

    def save(self, *args, **kwargs):
        if self.id and not self.location_name:
            self.location_name = 'plot'
        if self.status == INACCESSIBLE:
            self.accessible = False
        else:
            if self.id:
                PlotLogEntry = django_apps.get_model(
                    *'plot.plotlogentry'.split('.'))
                try:
                    PlotLogEntry.objects.get(plot_log__plot__pk=self.id)
                except PlotLogEntry.DoesNotExist:
                    self.accessible = True
                except MultipleObjectsReturned:
                    pass
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.plot_identifier, )

    def common_clean(self):
        """Asserts the plot map_area is a valid map_area and that
        an enrolled plot cannot be unconfirmed.
        """
        if self.map_area not in site_mappers.map_areas:
            raise MapperError(
                f'Invalid map area. Got \'{self.map_area}\'. Site mapper expects one '
                f'of map_areas={site_mappers.map_areas}.')
        elif self.id:
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    raise PlotEnrollmentError(
                        'Plot is enrolled and may not be unconfirmed')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return (super().common_clean_exceptions
                + [PlotEnrollmentError, MapperError])

    @property
    def identifier_segment(self):
        return self.plot_identifier[:-3]

    @property
    def community(self):
        return self.map_area

    class Meta:
        app_label = 'plot'
        ordering = ['-plot_identifier', ]
        unique_together = (('gps_target_lat', 'gps_target_lon'),)
        household_model = 'household.household'
