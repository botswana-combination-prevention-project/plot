from plot.models import PlotLogEntry
from datetime import datetime


class PlotLogEntryViewMixin:

    def is_required(self, plot):
        plot_log_entry_required = True
        if not plot.confirmed:
            if not self.plot_log_entry_count(plot):
                plot_log_entries = PlotLogEntry.objects.filter(
                    plot_log__plot__plot_identifier=plot.plot_identifier).order_by('-created')
                for plot_log_entry in plot_log_entries:
                    if plot_log_entry.created.date() == datetime.today().date():
                        plot_log_entry_required = False
                        break
            else:
                plot_log_entry_required = False
        else:
            plot_log_entry_required = False
        return plot_log_entry_required

    def plot_log_entry_count(self, plot):
        plot_log_entries = PlotLogEntry.objects.filter(
            plot_log__plot__plot_identifier=plot.plot_identifier).count()
        return plot_log_entries == 3
