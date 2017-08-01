# coding=utf-8

from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch

from edc_base.modeladmin_mixins import audit_fieldset_tuple, audit_fields

from ..admin_site import plot_admin
from ..forms import PlotForm
from ..modeladmin_mixins import ModelAdminMixin
from ..models import Plot


@admin.register(Plot, site=plot_admin)
class PlotAdmin(ModelAdminMixin):

    form = PlotForm
    date_hierarchy = 'modified'
    list_per_page = 30
    list_max_show_all = 1000
    fieldsets = (
        (None, {'fields':
                ('plot_identifier',
                 'status',
                 'gps_confirmed_latitude',
                 'gps_confirmed_longitude',
                 'cso_number',
                 'household_count',
                 'eligible_members',
                 'time_of_week',
                 'time_of_day',
                 'description', 'comment')}),
        ('Location', {
            'classes': ('collapse',),
            'fields': (
                'location_name',
                'map_area',
                'gps_target_lat',
                'gps_target_lon',
                'target_radius')}),
        ('Categories', {
            'classes': ('collapse',),
            'fields': ('rss', 'htc', 'ess', 'selected')}),
        ('Enrollment', {
            'classes': ('collapse',),
            'fields': ('enrolled', 'enrolled_datetime')}),
        audit_fieldset_tuple,
    )

    radio_fields = {
        'status': admin.VERTICAL,
        'time_of_week': admin.VERTICAL,
        'time_of_day': admin.VERTICAL,
    }

    list_display = (
        'plot_identifier',
        'status',
        'accessible',
        'confirmed',
        'rss',
        'htc',
        'ess',
        'enrolled',
        'household_count',
        'enrolled_datetime',
        'eligible_members',
        'modified',
        'user_modified',
        'hostname_modified')

    list_filter = (
        'accessible',
        'confirmed',
        'rss',
        'htc',
        'ess',
        'enrolled',
        'status',
        'created',
        'modified',
        'map_area',
        'access_attempts',
        'hostname_modified',
        'section',
        'sub_section',
        'selected',
        'time_of_week',
        'time_of_day')

    search_fields = (
        'plot_identifier',
        'cso_number',
        'map_area',
        'section',
        'status',
        'id') + audit_fields

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + (
            'plot_identifier', 'htc', 'rss', 'selected',
            'enrolled', 'enrolled_datetime')

    def view_on_site(self, obj):
        try:
            return reverse(
                'plot:listboard_url',
                kwargs=dict(plot_identifier=obj.plot_identifier))
        except NoReverseMatch:
            return True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
