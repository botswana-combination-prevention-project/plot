# coding=utf-8

from django.conf.urls import url

from .admin_site import plot_admin

app_name = 'plot'

urlpatterns = [
    url(r'^admin/', plot_admin.urls),
]
