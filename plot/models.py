from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.db import models, IntegrityError, transaction, DatabaseError
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.choices import TIME_OF_WEEK, TIME_OF_DAY
from edc_identifier.exceptions import IdentifierError
from edc_map.site_mappers import site_mappers
from edc_subset_manager.manager_mixins import SubsetManagerMixin

from .choices import PLOT_STATUS, SELECTED
from .constants import CONFIRMED, UNCONFIRMED, RESIDENTIAL_NOT_HABITABLE, NON_RESIDENTIAL, INACCESSIBLE, ACCESSIBLE
from .model_mixins import GpsModelMixin
from .plot_identifier import PlotIdentifier


def is_valid_community(self, value):
        """Validates the community string against a list of site_mappers map_areas."""
        if value.lower() not in [l.lower() for l in site_mappers.map_areas]:
            raise ValidationError(u'{0} is not a valid community name.'.format(value))


class CommunitySubsetManagerError(Exception):
    pass


class CommunitySubsetManagerMixin(SubsetManagerMixin, models.Manager):

    reference_model = 'bcpp_household.plot'
    reference_attr = 'community'
    to_reference_model = ['household_structure', 'household', 'plot']
    reference_subset_attr = 'plot_identifier'

    @property
    def reference_value(self):
        return site_mappers.current_mapper.map_area


class PlotManager(CommunitySubsetManagerMixin, models.Manager):

    to_reference_model = []

    def get_by_natural_key(self, plot_identifier):
        return self.get(plot_identifier=plot_identifier)


class Plot(GpsModelMixin, BaseUuidModel):
    """A model completed by the user (and initially by the system) to represent a Plot
    in the community."""

    plot_identifier = models.CharField(
        verbose_name='Plot Identifier',
        max_length=25,
        unique=True,
        help_text="Plot identifier",
        editable=False,
        db_index=True)

    eligible_members = models.IntegerField(
        verbose_name="Approximate number of age eligible members",
        blank=True,
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
        null=True,
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
        null=True,
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

    action = models.CharField(
        max_length=25,
        null=True,
        default=UNCONFIRMED,
        editable=False)

    access_attempts = models.IntegerField(
        default=0,
        editable=False,
        help_text='Number of attempts to access a plot to determine it\'s status.')

    # Google map static images for this plots with different zoom levels.
    # uploaded_map_16, uploaded_map_17, uploaded_map_18 zoom level 16, 17, 18 respectively
    uploaded_map_16 = models.CharField(
        verbose_name="Map image at zoom level 16",
        max_length=25,
        null=True,
        blank=True,
        editable=False)

    uploaded_map_17 = models.CharField(
        verbose_name="Map image at zoom level 17",
        max_length=25,
        null=True,
        blank=True,
        editable=False)

    uploaded_map_18 = models.CharField(
        verbose_name="Map image at zoom level 18",
        max_length=25,
        null=True,
        blank=True,
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

    enrolled_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    htc = models.NullBooleanField(
        default=False,
        editable=False)

    objects = PlotManager()

    history = HistoricalRecords()

    def __str__(self):
        if site_mappers.get_mapper(site_mappers.current_community).clinic_plot_identifier == self.plot_identifier:
            return 'BCPP-CLINIC'
        else:
            return self.plot_identifier

    def natural_key(self):
        return (self.plot_identifier, )

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        update_fields = kwargs.get('update_fields')
        self.allow_enrollment(using, update_fields=update_fields)
        if not self.community:
            # plot data is imported and not entered, so community must be provided on import
            raise ValidationError('Attribute \'community\' may not be None for model {0}'.format(self))
        if self.household_count > settings.MAX_HOUSEHOLDS_PER_PLOT:
            raise ValidationError('Number of households cannot exceed {}. '
                                  'Perhaps catch this in the forms.py. See '
                                  'settings.MAX_HOUSEHOLDS_PER_PLOT'.format(settings.MAX_HOUSEHOLDS_PER_PLOT))
        # unless overridden, if self.community != to mapper.map_area, raise
        self.verify_plot_community_with_current_mapper(self.community)
        # if self.community does not get valid mapper, will raise an error that should be caught in forms.pyx
        mapper = site_mappers.get_mapper(site_mappers.current_community)
        if not self.plot_identifier:
            self.plot_identifier = PlotIdentifier(mapper.map_code, using).get_identifier()
            if not self.plot_identifier:
                raise IdentifierError('Expected a value for plot_identifier. Got None')
        self.action = self.get_action()
        try:
            update_fields = update_fields + ['action', 'distance_from_target', 'plot_identifier', 'user_modified']
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(Plot, self).save(*args, **kwargs)

    def get_identifier(self):
        return self.plot_identifier

    @property
    def identifier_segment(self):
        return self.plot_identifier[:-3]

    class Meta:
        app_label = 'bcpp_household'
        ordering = ['-plot_identifier', ]
        unique_together = (('gps_target_lat', 'gps_target_lon'),)
