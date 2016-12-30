# coding=utf-8

from django.conf.urls import url

from .admin_site import plot_admin
from .views import PlotsView

urlpatterns = [
    url(r'^admin/', plot_admin.urls),
    url(r'^list/(?P<page>\d+)/', PlotsView.as_view(), name='list_url'),
    url(r'^list/', PlotsView.as_view(), name='list_url'),
]
