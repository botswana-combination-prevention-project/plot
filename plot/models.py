from django.db import models
from django.core.validators import MaxValueValidator
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_map.site_mappers import site_mappers
from edc_map.model_mixins import MapperModelMixin

from edc_base.model.validators.date import datetime_not_future

from bcpp.manager_mixins import BcppSubsetManagerMixin
from survey.validators import date_in_survey

from .choices import PLOT_STATUS, SELECTED, PLOT_LOG_STATUS, INACCESSIBILITY_REASONS
from .helper import Helper
from .validators import is_valid_community


class PlotManager(BcppSubsetManagerMixin, models.Manager):

    reference_model = 'plot.plot'
    to_reference_model = ['household_structure', 'household', 'plot']

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot_identifier=plot_identifier)


class PlotLogManager(BcppSubsetManagerMixin, models.Manager):

    lookup = ['plot']

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot__plot_identifier=plot_identifier)


class PlotLogEntryManager(BcppSubsetManagerMixin, models.Manager):

    lookup = ['plot_log', 'plot']

    def get_by_natural_key(self, report_datetime, plot_identifier):
        return self.get(report_datetime=report_datetime, plot__plot_identifier=plot_identifier)


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

    # objects = PlotManager()

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


class PlotLog(BaseUuidModel):
    """A system model to track an RA\'s attempts to confirm a Plot (related)."""

    plot = models.OneToOneField(Plot)

    history = HistoricalRecords()

    # objects = PlotLogManager()

    def __str__(self):
        return str(self.plot)

    def natural_key(self):
        return self.plot.natural_key()
    natural_key.dependencies = ['plot.plot']

    class Meta:
        app_label = 'plot'


class PlotLogEntry(BaseUuidModel):
    """A model completed by the user to track an RA\'s attempts to confirm a Plot."""
    plot_log = models.ForeignKey(PlotLog)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        validators=[datetime_not_future, date_in_survey])

    log_status = models.CharField(
        verbose_name='What is the status of this plot?',
        max_length=25,
        choices=PLOT_LOG_STATUS)

    reason = models.CharField(
        verbose_name='If inaccessible, please indicate the reason.',
        max_length=25,
        blank=True,
        null=True,
        choices=INACCESSIBILITY_REASONS)

    reason_other = models.CharField(
        verbose_name='If Other, specify',
        max_length=100,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        verbose_name="Comments",
        max_length=250,
        null=True,
        blank=True,
        help_text=('IMPORTANT: Do not include any names or other personally identifying '
                   'information in this comment'))

    # objects = PlotLogEntryManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, ) + self.plot_log.natural_key()
    natural_key.dependencies = ['plot.plot_log']

    def __str__(self):
        return '{} ({})'.format(self.plot_log, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        app_label = 'plot'
        unique_together = ('plot_log', 'report_datetime')
