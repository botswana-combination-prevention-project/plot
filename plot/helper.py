import pytz

from django.apps import apps as django_apps

from edc_constants.constants import CLOSED
from edc_map.site_mappers import site_mappers
from edc_device.constants import CLIENT
from edc_base.utils import get_utcnow

from .plot_identifier import PlotIdentifier

app_config = django_apps.get_app_config('plot')
edc_device_app_config = django_apps.get_app_config('edc_device')


class PlotHelperError(Exception):
    pass


class MaxHouseholdsExceededError(Exception):
    pass


class Helper:

    def __init__(self, plot):
        for field in plot._meta.get_fields():
            attr = field.name
            try:
                field.to  # avoid relation fields
            except AttributeError:
                attr = 'plot_id' if attr == 'id' else attr
                setattr(self, attr, getattr(plot, field.name))

    def get_identifier(self):
        identifier = self.plot_identifier
        if not identifier:
            if edc_device_app_config.role == CLIENT:
                identifier = PlotIdentifier(
                    study_site=site_mappers.get_mapper(site_mappers.current_map_area).map_code,
                ).identifier
            else:
                raise PlotHelperError(
                    'Blocking attempt to create identifier on non-client device. Got device is \'{}\''.format(
                        edc_device_app_config.role))
        return identifier

    def validate(self):
        if edc_device_app_config.role == CLIENT:
            # do not allow access to HTC plots
            if not self.plot_id and edc_device_app_config.role == CLIENT and self.htc:
                raise PlotHelperError(
                    'Blocking attempt to modify plot assigned to the HTC campaign. Got {}.'.format(
                        self.plot_identifier))
            self.map_area_or_raise()
            self.enroll_or_raise()
            if self.household_count > app_config.max_households:
                raise MaxHouseholdsExceededError(
                    'Number of households per plot cannot exceed {}. '
                    'Perhaps catch this in the forms.py. See '
                    'plot.AppConfig'.format(app_config.max_households))

    def enroll_or_raise(self):
        """Raises an exception if enrollment is closed."""
        if not self.plot_id and edc_device_app_config.role == CLIENT:
            if app_config.enrollment.status == CLOSED:
                mapper_instance = site_mappers.get_mapper(site_mappers.current_map_area)
                if get_utcnow() > pytz.utc.localize(mapper_instance.current_survey_dates.full_enrollment_date):
                    raise PlotHelperError(
                        'Enrollment for {0} ended on {1}. This plot, and the '
                        'data related to it, may not be modified. '
                        'See site_mappers'.format(
                            self.community,
                            mapper_instance.current_survey_dates.full_enrollment_date.strftime('%Y-%m-%d')))

    def map_area_or_raise(self):
        """Returns True if the plot.community = the current mapper.map_area."""
        if edc_device_app_config.role == CLIENT:
            if self.community:
                if self.community != site_mappers.get_mapper(site_mappers.current_map_area).map_area:
                    raise PlotHelperError(
                        'Invalid community, expected \'{}\'. Got \'{}\'. '.format(
                            site_mappers.get_mapper(site_mappers.current_map_area).map_area, self.community))

#     def household_valid_to_delete(self, instance, using=None):
#         """ Checks whether there is a plot log entry for each log. If it does not exists the
#         household can be deleted. """
#         Household = django_apps.get_model('bcpp_household', 'Household')
#         HouseholdLogEntry = django_apps.get_model('bcpp_household', 'HouseholdLogEntry')
#         allowed_to_delete = []
#         for hh in Household.objects.using(using).filter(plot=instance):
#             if (HouseholdLogEntry.objects.filter(
#                     household_log__household_structure__household=hh).exists() or hh in allowed_to_delete):
#                 continue
#             allowed_to_delete.append(hh)
#         return allowed_to_delete
#
#     def validate_number_to_delete(self, instance, existing_no, using=None):
#             if (existing_no in [0, 1] or instance.household_count == existing_no or
#                     instance.household_count > existing_no or instance.household_count == 0):
#                 return False
#             else:
#                 if self.household_valid_to_delete(instance, using):
#                     del_valid = existing_no - instance.household_count
#                     if len(self.household_valid_to_delete(instance, using)) < del_valid:
#                         return len(self.household_valid_to_delete(instance, using))
#                     else:
#                         return del_valid
#                 return False
#
#     def delete_households_for_non_residential(self, instance, existing_no, using=None):
#         Household = django_apps.get_model('bcpp_household', 'Household')
#         HouseholdStructure = django_apps.get_model('bcpp_household', 'HouseholdStructure')
#         HouseholdLog = django_apps.get_model('bcpp_household', 'HouseholdLog')
#         household_to_delete = self.household_valid_to_delete(instance, using)
#         try:
#             if len(household_to_delete) == existing_no and existing_no > 0:
#                 hh = HouseholdStructure.objects.filter(household__in=household_to_delete)
#                 hl = HouseholdLog.objects.filter(household_structure__in=hh)
#                 hl.delete()  # delete household_logs
#                 hh.delete()  # delete household_structure
#                 for hh in household_to_delete:
#                     with transaction.atomic():
#                         Household.objects.get(id=hh.id).delete()  # delete household
#                 return True
#             else:
#                 return False
#         except IntegrityError:
#             return False
#         except DatabaseError:
#             return False
#
#     def delete_household(self, instance, existing_no, using=None):
#         Household = django_apps.get_model('bcpp_household', 'Household')
#         HouseholdStructure = django_apps.get_model('bcpp_household', 'HouseholdStructure')
#         HouseholdLog = django_apps.get_model('bcpp_household', 'HouseholdLog')
#         try:
#             delete_no = self.validate_number_to_delete(
#                 instance, existing_no, using) if self.validate_number_to_delete(
#                 instance,
#                 existing_no,
#                 using) else 0
#             if not delete_no == 0:
#                 deletes = self.household_valid_to_delete(instance, using)[:delete_no]
#                 hh = HouseholdStructure.objects.filter(household__in=deletes)
#                 hl = HouseholdLog.objects.filter(household_structure__in=hh)
#                 hl.delete()  # delete household_logs
#                 hh.delete()  # delete household_structure
#                 for hh in deletes:
#                     with transaction.atomic():
#                         Household.objects.get(id=hh.id).delete()  # delete household
#                 return True
#             else:
#                 return False
#         except IntegrityError:
#             return False
#         except DatabaseError:
#             return False
#
#     def delete_confirmed_household(self, instance, existing_no, using=None):
#         """ Deletes required number of households. """
#         if instance.status in [RESIDENTIAL_NOT_HABITABLE, NON_RESIDENTIAL]:
#             return self.delete_households_for_non_residential(instance, existing_no, using)
#         else:
#             return self.delete_household(instance, existing_no, using)
#
#     def safe_delete_households(self, existing_no, instance=None, using=None):
#         """ Deletes households and HouseholdStructure if member_count==0 and no log entry.
#             If there is a household log entry, this DOES NOT delete the household
#         """
#         instance = instance or self
#         using = using or 'default'
#         return self.delete_confirmed_household(instance, existing_no)
#
#     def create_or_delete_households(self, instance=None, using=None):
#         """Creates or deletes households to try to equal the number of households reported on the plot instance.
#
#         This gets called by a household post_save signal and on the plot save method on change.
#
#             * If number is greater than actual household instances, households are created.
#             * If number is less than actual household instances, households are deleted as long as
#               there are no household members and the household log does not have entries.
#             * bcpp_clinic is a special case to allow for a plot to represent the BCPP Clinic."""
#         instance = instance or self
#         using = using or 'default'
#         Household = django_apps.get_model('bcpp_household', 'Household')
#         # check that tuple has not changed and has "residential_habitable"
#         if instance.status:
#             if instance.status not in [item[0] for item in list(PLOT_STATUS) + [('bcpp_clinic', 'BCPP Clinic')]]:
#                 raise AttributeError('{0} not found in choices tuple PLOT_STATUS. {1}'.format(instance.status,
#                                                                                               PLOT_STATUS))
#         existing_household_count = Household.objects.using(using).filter(plot__pk=instance.pk).count()
#         instance.create_household(instance.household_count - existing_household_count, using=using)
#         instance.safe_delete_households(existing_household_count, using=using)
#         with transaction.atomic():
#             count = Household.objects.using(using).filter(plot__pk=instance.pk).count()
#         return count
#
#     @property
#     def validate_plot_accessible(self):
#         if self.plot_log_entry and (self.plot_inaccessible is False) and self.plot_log_entry.log_status == ACCESSIBLE:
#             return True
#         return False
#
#     def gps(self):
#         return "S{0} {1} E{2} {3}".format(self.gps_degrees_s, self.gps_minutes_s,
#                                           self.gps_degrees_e, self.gps_minutes_e)
#
#     def get_contained_households(self):
#         from bcpp_household.models import Household
#         households = Household.objects.filter(plot__plot_identifier=self.plot_identifier)
#         return households
#
#     @property
#     def log_form_label(self):
#         # TODO: where is this used?
#         using = 'default'
#         PlotLog = django_apps.get_model('bcpp_household', 'PlotLog')
#         PlotLogEntry = django_apps.get_model('bcpp_household', 'PlotLogEntry')
#         form_label = []
#         try:
#             plot_log = PlotLog.objects.using(using).get(plot=self)
#             for plot_log_entry in PlotLogEntry.objects.using(
#                     using).filter(plot_log=plot_log).order_by('report_datetime'):
#                 try:
#                     form_label.append((plot_log_entry.log_status.lower() + '-' +
#                                        plot_log_entry.report_datetime.strftime('%Y-%m-%d'), plot_log_entry.id))
#                 except AttributeError:  # log_status is None ??
#                     form_label.append((plot_log_entry.report_datetime.strftime('%Y-%m-%d'), plot_log_entry.id))
#         except PlotLog.DoesNotExist:
#             pass
#         if self.access_attempts < 3 and self.action != CONFIRMED:
#             form_label.append(('add new entry', 'add new entry'))
#         if not form_label and self.action != CONFIRMED:
#             form_label.append(('add new entry', 'add new entry'))
#         return form_label
#
#     @property
#     def log_entry_form_urls(self):
#         # TODO: where is this used?
#         # TODO: this does not belong on the plot model!
#         """Returns a url or urls to the plotlogentry(s) if an instance(s) exists."""
#         using = 'default'
#         PlotLog = django_apps.get_model('bcpp_household', 'PlotLog')
#         PlotLogEntry = django_apps.get_model('bcpp_household', 'PlotLogEntry')
#         entry_urls = {}
#         try:
#             plot_log = PlotLog.objects.using(using).get(plot=self)
#             for entry in PlotLogEntry.objects.using(using).filter(plot_log=plot_log).order_by('report_datetime'):
#                 entry_urls[entry.pk] = self._get_form_url('plotlogentry', entry.pk)
#             add_url_2 = self._get_form_url('plotlogentry', model_pk=None, add_url=True)
#             entry_urls['add new entry'] = add_url_2
#         except PlotLog.DoesNotExist:
#             pass
#         return entry_urls
#
#     def _get_form_url(self, model, model_pk=None, add_url=None):
#         url = ''
#         pk = None
#         app_label = 'bcpp_household'
#         if add_url:
#             url = reverse('admin:{0}_{1}_add'.format(app_label, model))
#             return url
#         if not model_pk:  # This is a like a SubjectAbsentee
#             model_class = django_apps.get_model(app_label, model)
#             try:
#                 pk = model_class.objects.get(plot=self).pk
#             except model_class.DoesNotExist:
#                 pk = None
#         else:
#             pk = model_pk
#         if pk:
#             url = reverse('admin:{0}_{1}_change'.format(app_label, model), args=(pk, ))
#         else:
#             url = reverse('admin:{0}_{1}_add'.format(app_label, model))
#         return url
#
#     @property
#     def location(self):
#         if self.plot_identifier.endswith('0000-00'):
#             return 'clinic'
#         else:
#             return 'household'
#
#     @property
#     def plot_inaccessible(self):
#         """Returns True if the plot is inaccessible as defined by its status and number of attempts."""
#         PlotLogEntry = django_apps.get_model('bcpp_household', 'plotlogentry')
#         return PlotLogEntry.objects.filter(plot_log__plot__id=self.id, log_status=INACCESSIBLE).count() >= 3
#
#     @property
#     def target_radius_in_meters(self):
#         return self.target_radius * 1000
#
#     @property
#     def plot_log(self):
#         """Returns an instance of the plot log."""
#         PlotLog = django_apps.get_model('bcpp_household', 'plotlog')
#         try:
#             instance = PlotLog.objects.get(plot__id=self.id)
#         except PlotLog.DoesNotExist:
#             instance = None
#         return instance
#
#     @property
#     def plot_log_entry(self):
#         PlotLogEntry = django_apps.get_model('bcpp_household', 'plotlogentry')
#         try:
#             return PlotLogEntry.objects.filter(plot_log__plot__id=self.id).latest('report_datetime')
#         except PlotLogEntry.DoesNotExist:
#             pass
