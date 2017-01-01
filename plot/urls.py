# coding=utf-8

from django.conf.urls import url

from edc_constants.constants import UUID_PATTERN

from plot.patterns import plot_identifier

from .admin_site import plot_admin
from .views import PlotsView, LocationView

urlpatterns = [
    url(r'^admin/', plot_admin.urls),
    url(r'^list/(?P<page>\d+)/', PlotsView.as_view(), name='list_url'),
    url(r'^list/(?P<plot_identifier>' + plot_identifier + ')/', PlotsView.as_view(), name='list_url'),
    url(r'^list/(?P<id>' + UUID_PATTERN.pattern + ')/', PlotsView.as_view(), name='list_url'),
    url(r'^list/', PlotsView.as_view(), name='list_url'),
    url(r'^map/(?P<map_area>\w+)/(?P<plot_identifier>' + plot_identifier + ')/',
        LocationView.as_view(), name='map_url'),
]
