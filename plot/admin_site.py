from django.contrib.admin import AdminSite


class PlotAdminSite(AdminSite):
    site_title = 'Plot'
    site_header = 'Plot'
    index_title = 'Plot'
    site_url = '/'
plot_admin = PlotAdminSite(name='plot_admin')
