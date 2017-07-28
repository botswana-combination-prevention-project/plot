# coding=utf-8

from django.contrib import admin

from edc_base.modeladmin_mixins import audit_fieldset_tuple

from ..admin_site import plot_admin
from ..forms import PlotLogForm
from ..modeladmin_mixins import ModelAdminMixin
from ..models import PlotLog


@admin.register(PlotLog, site=plot_admin)
class PlotLogAdmin(ModelAdminMixin):
    form = PlotLogForm
    instructions = []
    date_hierarchy = 'modified'
    list_per_page = 15
    list_display = (
        'plot',
        'modified', 'user_modified', 'hostname_modified')

    fieldsets = (
        (None, {'fields': ('plot', )}), audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + ('plot', )

    search_fields = ('plot__plot_identifier', 'plot__pk')
    list_filter = ('hostname_created', 'modified', 'user_modified')
