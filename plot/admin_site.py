# coding=utf-8

from django.contrib.admin import AdminSite


class PlotAdminSite(AdminSite):
    site_title = 'Plot'
    site_header = 'Plot'
    index_title = 'Plot'
    site_url = '/plot/listboard/'


plot_admin = PlotAdminSite(name='plot_admin')
