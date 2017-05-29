# coding=utf-8

from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_constants.utils import get_display

from .choices import PLOT_STATUS
from .constants import INACCESSIBLE, ACCESSIBLE, RESIDENTIAL_HABITABLE
from .models import Plot, PlotLog, PlotLogEntry


class PlotForm(CommonCleanModelFormMixin, forms.ModelForm):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None

    plot_identifier = forms.CharField(
        label='Plot identifier',
        required=True,
        help_text='This field is read only.',
        widget=forms.TextInput(attrs={'size': 15, 'readonly': True}))

    def clean(self):
        cleaned_data = super().clean()
        app_config = django_apps.get_app_config('plot')
        if not self.instance.id:
            if not app_config.allow_add_plot(cleaned_data.get('map_area')):
                raise forms.ValidationError(
                    'Plots may not be added in this community. '
                    'Got \'{}\'.'.format(
                        cleaned_data.get('map_area')))
            else:
                if not cleaned_data.get('ess'):
                    raise forms.ValidationError(
                        'Only ESS plots may be added. See Categories.')
                if cleaned_data.get('status') != RESIDENTIAL_HABITABLE:
                    raise forms.ValidationError(
                        'Only {} plots may be added.'.format(
                            get_display(PLOT_STATUS, RESIDENTIAL_HABITABLE)))
        else:
            if cleaned_data.get('location_name') in app_config.special_locations:
                raise forms.ValidationError(
                    'Plot may not be changed by a user. Plot location '
                    'name == \'{}\''.format(
                        cleaned_data.get('location_name')))
            try:
                PlotLogEntry.objects.exclude(
                    log_status=INACCESSIBLE).get(
                        plot_log__plot__pk=self.instance.id)
            except PlotLogEntry.DoesNotExist:
                raise forms.ValidationError(
                    'Plot log entry is required before attempting '
                    'to modify a plot.')
            except MultipleObjectsReturned:
                pass
        self.validation_for_radius_increase()
        self.household_count()
        self.eligible_members()
        self.best_time_to_visit()
        return cleaned_data

    class Meta:
        model = Plot
        fields = '__all__'

    def eligible_members(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get('status') != RESIDENTIAL_HABITABLE
                and cleaned_data.get('eligible_members')):
            raise forms.ValidationError(
                {'eligible_members': 'Must be zero if not {}'.format(
                    get_display(PLOT_STATUS, RESIDENTIAL_HABITABLE))})
        elif (cleaned_data.get('eligible_members')
              and not cleaned_data.get('household_count')):
            raise forms.ValidationError(
                {'eligible_members': 'Must be zero if no households'})

    def household_count(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get('status') != RESIDENTIAL_HABITABLE
                and cleaned_data.get('household_count')):
            raise forms.ValidationError(
                {'household_count': 'Must be zero if no households'})
        elif (cleaned_data.get('status') == RESIDENTIAL_HABITABLE
              and not cleaned_data.get('household_count')):
            raise forms.ValidationError(
                {'household_count': 'May not be zero if {}'.format(
                    get_display(PLOT_STATUS, RESIDENTIAL_HABITABLE))})

    def best_time_to_visit(self):
        """Raise if time of the day is not specified for eligible members.
         """
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('eligible_members'):
            if cleaned_data.get('time_of_week'):
                raise forms.ValidationError(
                    {'time_of_week': 'Not required for if no eligible members'})
            if cleaned_data.get('time_of_day'):
                raise forms.ValidationError(
                    {'time_of_day': 'Not required for if no eligible members'})
        elif cleaned_data.get('eligible_members'):
            if not cleaned_data.get('time_of_day'):
                raise forms.ValidationError(
                    {'time_of_day': 'Required for if eligible members'})
            if not cleaned_data.get('time_of_week'):
                raise forms.ValidationError(
                    {'time_of_week': 'Required for if eligible members'})

    def validation_for_radius_increase(self):
        cleaned_data = self.cleaned_data
        app_config = django_apps.get_app_config('plot')
        try:
            is_superuser = self.current_user.is_superuser
        except AttributeError:
            forms.ValidationError(
                {'target_radius': 'You do not have the right permission '
                 'to edit this field. User unknown.'})
        else:
            if (not is_superuser and not self.current_user.groups.filter(
                    name__in=app_config.supervisor_groups).exists()):
                if cleaned_data.get('target_radius') != self.instance.target_radius:
                    raise forms.ValidationError(
                        {'target_radius': 'You do not have the right permission '
                         'to edit this field.'})
        return cleaned_data


class PlotLogForm(CommonCleanModelFormMixin, forms.ModelForm):

    class Meta:
        model = PlotLog
        fields = '__all__'


class PlotLogEntryForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super(PlotLogEntryForm, self).clean()
        plot_log = cleaned_data.get('plot_log')
        status = cleaned_data.get('log_status')
        if status == INACCESSIBLE and plot_log.plot.confirmed:
            raise forms.ValidationError(
                {'log_status':
                 'This plot has been \'confirmed\'. Cannot be inaccessible.'})
        if status == ACCESSIBLE:
            if cleaned_data.get('reason'):
                raise forms.ValidationError(
                    {'reason': 'Reason is not required if accessible.'})
            if cleaned_data.get('reason_other'):
                raise forms.ValidationError(
                    {'reason_other': 'Not required if plot is accessible.'})
        return cleaned_data

    class Meta:
        model = PlotLogEntry
        fields = '__all__'
        localized_fields = ['report_datetime']
