# coding=utf-8

from django.conf.urls import url

from .admin_site import plot_admin

urlpatterns = [
    url(r'^admin/', plot_admin.urls),
    # url(r'', admin.site.urls),
]
