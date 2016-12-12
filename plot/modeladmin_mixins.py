from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_base.modeladmin_mixins import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminReadOnlyMixin, ModelAdminAuditFieldsMixin)


class ModelAdminMixin(ModelAdminFormInstructionsMixin, ModelAdminNextUrlRedirectMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin, ModelAdminAuditFieldsMixin,
                      ModelAdminReadOnlyMixin, admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
