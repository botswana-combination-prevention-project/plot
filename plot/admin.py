# coding=utf-8

from django.contrib import admin

from .admin_site import plot_admin
from .forms import PlotLogForm, PlotLogEntryForm, PlotForm
from .models import Plot, PlotLogEntry, PlotLog

from .modeladmin_mixins import ModelAdminMixin


@admin.register(Plot, site=plot_admin)
class PlotAdmin(ModelAdminMixin):

    form = PlotForm
    date_hierarchy = 'modified'
    list_per_page = 30
    list_max_show_all = 1000
    fieldsets = (
        (None, {'fields':
                ['plot_identifier', 'status', 'gps_confirmed_latitude', 'gps_confirmed_longitude',
                 'cso_number', 'household_count', 'eligible_members', 'time_of_week', 'time_of_day',
                 'description', 'comment']}),
        ('Advanced options', {  # TODO: (selected field) is added temporarily to add plot manually. IT should be removed.
            'classes': ('collapse',),
            'fields': ['location_name', 'htc', 'map_area', 'selected', 'gps_target_lat', 'gps_target_lon', 'target_radius',
                       ]}),
    )

    list_display = (
        'plot_identifier', 'status', 'accessible', 'confirmed', 'htc', 'enrolled', 'household_count',
        'enrolled_datetime', 'eligible_members', 'modified', 'user_modified', 'hostname_modified')

#     list_display = ('plot_identifier', 'community', 'action', 'status', 'access_attempts', 'bhs', 'htc',
#                     'created', 'modified')
    list_filter = ('accessible', 'confirmed', 'enrolled', 'htc', 'status', 'created', 'modified', 'map_area',
                   'access_attempts', 'hostname_modified',
                   'section', 'sub_section', 'selected', 'time_of_week', 'time_of_day')

    search_fields = ('plot_identifier', 'cso_number', 'map_area', 'section', 'id')

    readonly_fields = ('plot_identifier', )
    radio_fields = {
        'status': admin.VERTICAL,
        'time_of_week': admin.VERTICAL,
        'time_of_day': admin.VERTICAL,
        'selected': admin.VERTICAL,  # TODO: (selected field) is added temporarily to add plot manually.
    }


@admin.register(PlotLogEntry, site=plot_admin)
class PlotLogEntryAdmin(ModelAdminMixin):
    form = PlotLogEntryForm
    date_hierarchy = 'modified'
    fields = ('plot_log', 'report_datetime', 'log_status', 'reason', 'reason_other', 'comment')
    list_per_page = 15
    list_display = ('plot_log', 'log_status', 'report_datetime')
    list_filter = ('log_status', 'report_datetime', 'plot_log__plot__map_area', 'log_status')
    search_fields = ('log_status', 'plot_log__plot__map_area', 'plot_log__plot__plot_identifier')
    radio_fields = {
        'reason': admin.VERTICAL,
        'log_status': admin.VERTICAL
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plot_log":
            if request.GET.get('plot_log'):
                kwargs["queryset"] = PlotLog.objects.filter(id__exact=request.GET.get('plot_log', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('plot_log')
                except ValueError:
                    self.readonly_fields.append('plot_log')
        return super(PlotLogEntryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PlotLogEntryInline(admin.TabularInline):
    model = PlotLogEntry
    form = PlotLogEntryForm
    extra = 0
    max_num = 5


@admin.register(PlotLog, site=plot_admin)
class PlotLogAdmin(ModelAdminMixin):
    form = PlotLogForm
    instructions = []
    inlines = [PlotLogEntryInline, ]
    date_hierarchy = 'modified'
    list_per_page = 15
    list_display = (
        'plot',
        'modified', 'user_modified', 'hostname_modified')
    readonly_fields = ('plot', )
    search_fields = ('plot__plot_identifier', 'plot__pk')
    list_filter = ('hostname_created', 'modified', 'user_modified')
