# coding=utf-8

from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .constants import INACCESSIBLE, ACCESSIBLE
from .models import Plot, PlotLog, PlotLogEntry


@receiver(post_save, weak=False, sender=Plot,
          dispatch_uid="plot_creates_households_on_post_save")
def plot_creates_households_on_post_save(
        sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw and not update_fields:
        instance.create_or_delete_households()
        if created:
            app_config = django_apps.get_app_config('plot')
            if not app_config.excluded_plot(instance):
                plot_log = PlotLog.objects.create(
                    plot=instance,
                    report_datetime=instance.report_datetime)
                if instance.ess:
                    PlotLogEntry.objects.create(
                        plot_log=plot_log,
                        log_status=ACCESSIBLE,
                        report_datetime=instance.report_datetime)


@receiver(post_save, weak=False, sender=PlotLogEntry,
          dispatch_uid="update_plot_on_post_save")
def update_plot_on_post_save(sender, instance, raw, created,
                             using, **kwargs):
    if not raw:
        plot = Plot.objects.get(pk=instance.plot_log.plot.pk)
        if created:
            plot.access_attempts = (plot.access_attempts or 0) + 1
        if instance.log_status == INACCESSIBLE:
            plot.accessible = False
            plot.gps_confirmed_latitude = None
            plot.gps_confirmed_longitude = None
            plot.distance_from_target = None
            plot.household_count = 0
        elif instance.log_status == ACCESSIBLE:
            plot.accessible = True
        plot.save()


@receiver(post_delete, weak=False, sender=PlotLogEntry,
          dispatch_uid="update_plot_on_plot_log_entry_post_delete")
def update_plot_on_plot_log_entry_post_delete(sender, instance, using, **kwargs):
    plot = Plot.objects.get(pk=instance.plot_log.plot.pk)
    plot.access_attempts = (plot.access_attempts or 0) - 1
    plot.access_attempts = 0 if plot.access_attempts < 1 else plot.access_attempts
    if plot.access_attempts == 0:
        plot.accessible = True
        plot.household_count = 0
        plot.eligible_members = 0
        plot.status = None
        plot.time_of_day = None
        plot.time_of_week = None
    plot.save()
