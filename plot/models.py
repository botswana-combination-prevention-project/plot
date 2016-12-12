from django.db import models
from django.core.validators import MaxValueValidator
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_map.site_mappers import site_mappers
from edc_map.model_mixins import MapperModelMixin

from bcpp.manager_mixins import BcppSubsetManagerMixin

from .choices import PLOT_STATUS, SELECTED
from .helper import Helper
from .validators import is_valid_community


class PlotManager(BcppSubsetManagerMixin, models.Manager):

    reference_model = 'plot.plot'
    to_reference_model = ['household_structure', 'household', 'plot']

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot_identifier=plot_identifier)


class Plot(MapperModelMixin, BaseUuidModel):
    """A model completed by the user (and initially by the system) to represent a Plot
    in the community."""

    plot_identifier = models.CharField(
        verbose_name='Plot Identifier',
        max_length=25,
        unique=True,
        help_text="Plot identifier",
        editable=False)

    eligible_members = models.IntegerField(
        verbose_name="Approximate number of age eligible members",
        null=True,
        help_text=(("Provide an approximation of the number of people "
                    "who live in this residence who are age eligible.")))

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

    cso_number = EncryptedCharField(
        verbose_name="CSO Number",
        blank=True,
        null=True,
        help_text=("provide the CSO number or leave BLANK."))

    household_count = models.IntegerField(
        verbose_name="Number of Households on this plot.",
        default=0,
        validators=[MaxValueValidator(9)],
        help_text=("Provide the number of households in this plot."))

    time_of_week = models.CharField(
        verbose_name='Time of week when most of the eligible members will be available',
        max_length=25,
        choices=TIME_OF_WEEK,
        blank=True,
        null=True)

    time_of_day = models.CharField(
        verbose_name='Time of day when most of the eligible members will be available',
        max_length=25,
        choices=TIME_OF_DAY,
        blank=True,
        null=True)

    status = models.CharField(
        verbose_name='Plot status',
        max_length=35,
        choices=PLOT_STATUS)

    target_radius = models.FloatField(
        default=.025,
        help_text='km',
        editable=False)

    distance_from_target = models.FloatField(
        null=True,
        editable=True,
        help_text='distance in meters')

    # 20 percent plots is reperesented by 1 and 5 percent of by 2, the rest of
    # the plots which is 75 percent selected value is None
    selected = models.CharField(
        max_length=25,
        null=True,
        verbose_name='selected',
        choices=SELECTED,
        editable=False)

    device_id = models.CharField(
        max_length=2,
        null=True,
        editable=False)

    confirmed = models.CharField(
        max_length=25,
        null=True,
        default=False,
        editable=False)

    access_attempts = models.IntegerField(
        default=0,
        help_text='Number of attempts to access a plot to determine it\'s status.',
        editable=False)

    community = models.CharField(
        max_length=25,
        help_text='If the community is incorrect, please contact the DMC immediately.',
        validators=[is_valid_community, ],
        editable=False)

    section = models.CharField(
        max_length=25,
        null=True,
        verbose_name='Section',
        editable=False)

    sub_section = models.CharField(
        max_length=25,
        null=True,
        verbose_name='Sub-section',
        help_text=u'',
        editable=False)

    bhs = models.NullBooleanField(
        default=None,
        editable=False,
        help_text=('True indicates that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    htc = models.NullBooleanField(
        default=False,
        editable=False)

    enrolled_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    objects = PlotManager()

    history = HistoricalRecords()

    def __str__(self):
        if site_mappers.get_mapper(site_mappers.current_map_area).clinic_plot_identifier == self.plot_identifier:
            return 'BCPP-CLINIC'
        else:
            return self.plot_identifier

    def natural_key(self):
        return (self.plot_identifier, )

    def save(self, *args, **kwargs):
        helper = Helper(self)
        helper.validate()
        if not self.plot_identifier:
            self.plot_identifier = helper.get_identifier()
        if self.gps_confirm_longitude and self.gps_confirm_latitude:
            self.confirmed = True
        else:
            self.confirmed = False
        super(Plot, self).save(*args, **kwargs)

    @property
    def identifier_segment(self):
        return self.plot_identifier[:-3]

    class Meta:
        app_label = 'plot'
        ordering = ['-plot_identifier', ]
        unique_together = (('gps_target_lat', 'gps_target_lon'),)
