# coding=utf-8

from django.conf.urls import url

from plot.patterns import plot_identifier

from .admin_site import plot_admin
from .views import PlotsView

urlpatterns = [
    url(r'^admin/', plot_admin.urls),
    url(r'^list/(?P<page>\d+)/', PlotsView.as_view(), name='list_url'),
    url(r'^list/(?P<plot_identifier>' + plot_identifier + ')/', PlotsView.as_view(), name='list_url'),
    url(r'^list/(?P<id>[0-9A-Za-z_\-]+)/', PlotsView.as_view(), name='list_url'),
    url(r'^list/', PlotsView.as_view(), name='list_url'),
]
