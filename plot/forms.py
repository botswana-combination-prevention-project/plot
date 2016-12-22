# coding=utf-8

from datetime import datetime

from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from django.forms.utils import ErrorList

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_map.site_mappers import site_mappers

from .constants import INACCESSIBLE, CONFIRMED, ACCESSIBLE

from .models import Plot, PlotLog, PlotLogEntry


class PlotForm(CommonCleanModelFormMixin, forms.ModelForm):

    plot_identifier = forms.CharField(
        label='Plot identifier',
        required=True,
        help_text='This field is read only.',
        widget=forms.TextInput(attrs={'size': 15, 'readonly': True}))

    accessible = forms.BooleanField(
        label='Accessible',
        required=False,
        help_text='This field is read only.',
        widget=forms.CheckboxInput(attrs={'disabled': True}))

    def clean(self):
        cleaned_data = super().clean()
        app_config = django_apps.get_app_config('plot')
        if self.instance.id:
            if cleaned_data.get('location_name') in app_config.special_locations:
                raise forms.ValidationError(
                    'Plot may not be changed by a user. Plot location name == \'{}\''.format(
                        cleaned_data.get('location_name')))
            try:
                PlotLogEntry.objects.exclude(log_status=INACCESSIBLE).get(plot_log__plot__pk=self.instance.id)
            except PlotLogEntry.DoesNotExist:
                raise forms.ValidationError('Plot log entry is required before attempting to modify a plot.')
            except MultipleObjectsReturned:
                pass
        return cleaned_data

    class Meta:
        model = Plot
        fields = '__all__'

#         try:
#             self.instance.allow_enrollment('default',
#                                            plot_instance=Plot(**cleaned_data),
#                                            exception_cls=forms.ValidationError)
#         except AttributeError:
#             raise forms.ValidationError('System settings do not allow for this form to be '
#                                         'edited. (e.g. mapper, community, site_code, device)')
#         if self.instance.htc:
#             raise forms.ValidationError('Plot is not a BHS plot (htc=True).')
#         if not self.instance.community:
#             raise forms.ValidationError('Community may not be blank. Must be '
#                                         'one of {1}.'.format(self.instance.community,
#                                                              ', '.join(site_mappers.map_areas)))
#         if not self.instance.validate_plot_accessible:
#             raise forms.ValidationError('You cannot confirm a plot, plot log entry is set to inacccessible.')

#         if not (cleaned_data.get('household_count') and cleaned_data.get('status') in ['residential_habitable']):
#             raise forms.ValidationError(
#                 'Invalid number of households. Only plots that are residential habitable can have households.')

#         self.household_count_and_status(cleaned_data)
#         self.status_and_eligible_member(cleaned_data)
#         self.gps_coordinates_filled(cleaned_data)
#         self.gps_verification(cleaned_data)
#         self.complete_plot_log_entry(cleaned_data)
#         self.best_time_to_visit(cleaned_data)

    def household_count_and_status(self, cleaned_data):
        """Check if a residential_habitable plot has a household count greater than zero."""

        if (cleaned_data.get('household_count') == 0 and
                cleaned_data.get('status') in ['residential_habitable']) or (
                    cleaned_data.get('household_count') and not
                    cleaned_data.get('status') in ['residential_habitable']):
            raise forms.ValidationError('Invalid number of households for plot that is '
                                        '{0}. Got {1}.'.format(cleaned_data.get('status'),
                                                               cleaned_data.get('household_count')))

    def status_and_eligible_member(self, cleaned_data):
        """Check if the plot status is not residential_habitable number of eligible member is 0."""

        if not cleaned_data.get('status') == 'residential_habitable' and cleaned_data.get('eligible_members') > 0:
            raise forms.ValidationError('If the residence is not residential_habitable, '
                                        'number of eligible members should be 0. Got '
                                        '{0}'.format(cleaned_data.get('eligible_members')))

    def gps_coordinates_filled(self, cleaned_data):
        """Check of gps verification coordinates g=have been filled."""

        if (not cleaned_data.get('gps_degrees_s') and not cleaned_data.get('gps_minutes_s') and
                not cleaned_data.get('gps_degrees_e') and not cleaned_data.get('gps_minutes_e')):
            raise forms.ValidationError('The following fields must all be filled '
                                        'gps_degrees_s, gps_minutes_s, gps_degrees_e, '
                                        'gps_minutes_e. Got {0}, {1}, {2}, '
                                        '{3}'.format(cleaned_data.get('gps_degrees_s'),
                                                     cleaned_data.get('gps_minutes_s'),
                                                     cleaned_data.get('gps_degrees_e'),
                                                     cleaned_data.get('gps_minutes_e')))

    def gps_verification(self, cleaned_data):
        """Verify gps target location and check within community radius."""

        mapper_cls = site_mappers.registry.get(self.instance.community)
        mapper = mapper_cls()
        self.instance.verify_plot_community_with_current_mapper(
            self.instance.community, exception_cls=forms.ValidationError)
        gps_lat = mapper.get_gps_lat(cleaned_data.get('gps_degrees_s'), cleaned_data.get('gps_minutes_s'))
        gps_lon = mapper.get_gps_lon(cleaned_data.get('gps_degrees_e'), cleaned_data.get('gps_minutes_e'))
        mapper.verify_gps_location(gps_lat, gps_lon, forms.ValidationError)
        mapper.verify_gps_to_target(gps_lat, gps_lon, self.instance.gps_target_lat,
                                    self.instance.gps_target_lon, self.instance.target_radius,
                                    forms.ValidationError)

    def complete_plot_log_entry(self, cleaned_data):
        """Check if a plot log entry has been created before confirming a plot."""

        if (cleaned_data.get('gps_degrees_s') and
                cleaned_data.get('gps_minutes_s') and
                cleaned_data.get('gps_degrees_e') and
                cleaned_data.get('gps_minutes_e')):
            try:
                PlotLog.objects.get(plot=self.instance)
            except PlotLog.DoesNotExist:
                raise forms.ValidationError(
                    'Please add a plot log entry before saving')

    def best_time_to_visit(self, cleaned_data):
        """Raise an error if time of the day is specified if residence is NOT residential_habitable or not specific
         if residential_habitable.
         """

        if not cleaned_data.get('status') == 'residential_habitable' and (
                cleaned_data.get('time_of_week') or cleaned_data.get('time_of_day')):
            raise forms.ValidationError('If the residence is NOT residential_habitable, '
                                        'do not provide the best time to visit (e.g time of week, time of day).')
        if cleaned_data.get('status') == 'residential_habitable' and (
                not cleaned_data.get('time_of_week') or not cleaned_data.get('time_of_day')):
            raise forms.ValidationError('If the residence is residential_habitable, provide '
                                        'the best time to visit (e.g time of week, time of day).')


class PlotLogForm(forms.ModelForm):

    class Meta:
        model = PlotLog
        fields = '__all__'


class PlotLogEntryForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(PlotLogEntryForm, self).clean()
        plot_log = cleaned_data.get('plot_log')
        plot_log.plot.allow_enrollment('default',
                                       plot_instance=plot_log.plot,
                                       exception_cls=forms.ValidationError)
        # confirm that an inaccessible log entry is not entered against a confirmed plot.
        status = cleaned_data.get('log_status')
        if cleaned_data.get('rarely_present') == 'Yes' and cleaned_data.get('status') == 'PRESENT':
            raise forms.ValidationError('Members cannot be present and have the be rarely present.')
        if cleaned_data.get('rarely_present') == 'Yes' and cleaned_data.get('supervisor_vdc_confirm') == 'No':
            raise forms.ValidationError('There needs to be a confirmation from supervisor and VDC for a '
                                        'plot with rarely or seasonally present members.')
        if status == INACCESSIBLE and plot_log.plot.action == CONFIRMED:
            raise forms.ValidationError('This plot has been \'confirmed\'. You cannot set it as INACCESSIBLE.')

        if status == ACCESSIBLE:
            if cleaned_data.get('reason'):
                self._errors['reason'] = ErrorList([u'This field is not required.'])
                raise forms.ValidationError('Reason is not required if plot is accessible.')
            if cleaned_data.get('reason_other'):
                self._errors['reason_other'] = ErrorList([u'This field is not required.'])
                raise forms.ValidationError('Other reason is not required if plot is accessible.')
        if PlotLogEntry.objects.filter(
                created__year=datetime.today().year,
                created__month=datetime.today().month,
                created__day=datetime.today().day,
                plot_log__plot=plot_log.plot):
            if not self.instance.id:
                raise forms.ValidationError('The plot log entry has been added already.')

        return cleaned_data

    class Meta:
        model = PlotLogEntry
        fields = '__all__'
