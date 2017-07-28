# coding=utf-8

from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch

from edc_base.modeladmin_mixins import audit_fieldset_tuple, audit_fields

from ..admin_site import plot_admin
from ..forms import PlotLogEntryForm
from ..modeladmin_mixins import ModelAdminMixin
from ..models import PlotLogEntry, PlotLog


@admin.register(PlotLogEntry, site=plot_admin)
class PlotLogEntryAdmin(ModelAdminMixin):
    form = PlotLogEntryForm
    date_hierarchy = 'modified'
    fieldsets = (
        (None, {'fields': (
            'plot_log',
            'report_datetime',
            'log_status',
            'reason',
            'reason_other',
            'comment')}),
        audit_fieldset_tuple)

    list_per_page = 15
    list_display = (
        'plot_log',
        'log_status',
        'report_datetime')
    list_filter = (
        'log_status',
        'report_datetime',
        'plot_log__plot__map_area',
        'log_status')
    search_fields = (
        'log_status',
        'plot_log__plot__map_area',
        'plot_log__plot__plot_identifier') + audit_fields
    radio_fields = {
        'reason': admin.VERTICAL,
        'log_status': admin.VERTICAL
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plot_log":
            if request.GET.get('plot_log'):
                kwargs["queryset"] = PlotLog.objects.filter(
                    id__exact=request.GET.get('plot_log', 0))
            elif request.GET.get('plot_identifier'):
                kwargs["queryset"] = PlotLog.objects.filter(
                    plot__plot_identifier__exact=request.GET.get('plot_identifier', 0))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def view_on_site(self, obj):
        try:
            return reverse(
                'plot:listboard_url',
                kwargs=dict(plot_identifier=obj.plot_log.plot.plot_identifier))
        except NoReverseMatch:
            return True
