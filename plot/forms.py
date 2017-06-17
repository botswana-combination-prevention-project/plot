# coding=utf-8

from django import forms
from django.apps import apps as django_apps

from edc_base.modelform_mixins import CommonCleanModelFormMixin

from plot_form_validators import PlotFormValidator, PlotLogEntryFormValidator

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
        form_validator = PlotFormValidator(
            add_plot_map_areas=app_config.add_plot_map_areas,
            special_locations=app_config.special_locations,
            supervisor_groups=app_config.supervisor_groups,
            current_user=self.current_user,
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = Plot
        fields = '__all__'


class PlotLogForm(CommonCleanModelFormMixin, forms.ModelForm):

    class Meta:
        model = PlotLog
        fields = '__all__'


class PlotLogEntryForm(CommonCleanModelFormMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        form_validator = PlotLogEntryFormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.validate()
        return cleaned_data

    class Meta:
        model = PlotLogEntry
        fields = '__all__'
        localized_fields = ['report_datetime']
