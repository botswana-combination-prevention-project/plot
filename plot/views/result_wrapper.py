from django.apps import apps as django_apps


class DummyPlotLogEntry:
    def __init__(self, plot_log):
        self.plot_log = plot_log


class ResultWrapper:
    def __init__(self, obj):
        self.created = obj.created
        self.modified = obj.modified
        self.user_created = obj.user_created
        self.user_modified = obj.user_modified
        self.hostname_created = obj.hostname_created
        self.hostname_modified = obj.hostname_modified
        self.object_wrapper(obj)

    def object_wrapper(self, obj):
        """Wraps the main model instance, obj."""
        app_config = django_apps.get_app_config('plot')
        self.plot = obj
        self.households = obj.household_set.all().order_by('household_identifier')
        self.plot_log = self.plot.plotlog
        plot_log_entries = self.plot.plotlog.plotlogentry_set.all().order_by('-report_datetime')
        self.plot_log_entries = [self.log_object_wrapper(log_obj) for log_obj in plot_log_entries]
        plot_log_entry = plot_log_entries.filter(
            report_date=self.plot.modified.date()).order_by('report_datetime').last()
        self.plot_log_entry = self.log_object_wrapper(
            plot_log_entry or DummyPlotLogEntry(self.plot_log))
        self.excluded_plot = app_config.excluded_plot(self.plot)

    @property
    def querystring(self):
        return [
            'next={url_name},plot_identifier'.format(url_name='plot:list_url'),
            'plot_identifier={}'.format(self.plot_identifier),
            'plot_log={}'.format(self.plot_log.id)]

    def log_object_urls(self, log_obj):
        log_obj.add_url = 'plot:plot_admin:plot_plotlogentry_add'
        log_obj.change_url = 'plot:plot_admin:plot_plotlogentry_change'
        return log_obj

    def log_object_wrapper(self, log_obj):
        """Wraps the log enrty model instance.

        Adds urls and querystring for the history control and add and change urls."""
        log_obj = self.log_object_urls(log_obj)
        log_obj.querystring = '&'.join(self.querystring)
        return log_obj

    @property
    def plot_identifier(self):
        return self.plot.plot_identifier

#     @property
#     def household_identifier(self):
#         return self.household.plot_identifier

    @property
    def community_name(self):
        return ' '.join(self.plot.map_area.split('_'))
