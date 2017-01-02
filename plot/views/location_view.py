import json

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from edc_base.views import EdcBaseViewMixin
from edc_map.views import MapImageView

from ..models import Plot


class LocationView(EdcBaseViewMixin, MapImageView):

    item_model = Plot
    item_model_field = 'plot_identifier'
    filename_field = 'plot_identifier'
    zoom_levels = django_apps.get_app_config('edc_map').zoom_levels
    map_image_view_base_html = 'bcpp/base.html'

    def point(self, obj):
        if obj.confirmed:
            return obj.confirmed_point
        return obj.target_point

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            site_header=admin.site.site_header,
            back_subject_url=reverse(
                'plot:list_url', kwargs=dict(plot_identifier=self.kwargs.get('plot_identifier'))),
#             back_call_url=reverse(
#                 'edc_call_manager_admin:call_manager_call_changelist') +
#             '?q=' + self.kwargs.get('plot_identifier'),
            add_point_url=reverse('plot:plot_admin:plot_plot_add')
        )
        # add new items to the json_data object
        data = dict(
            back_subject_url=context['back_subject_url'],
            # back_call_url=context['back_call_url'],
            add_point_url=context['add_point_url'],
            **json.loads(context['json_data']))
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        context.update(
            json_data=json_data,
            item_label=format_html('<i class="fa fa-building-o fa-lg"></i>'),
            item_title='Plot',
            navbar_selected='plot')
        return context
