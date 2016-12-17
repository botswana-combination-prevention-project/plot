# coding=utf-8

from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Plot, PlotLog, PlotLogEntry
from plot.constants import INACCESSIBLE, ACCESSIBLE
from django.core.exceptions import MultipleObjectsReturned


@receiver(post_save, weak=False, sender=Plot, dispatch_uid="create_households_on_post_save")
def create_households_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        instance.create_or_delete_households()
        if created:
            app_config = django_apps.get_app_config('plot')
            if not app_config.excluded_plot(instance):
                PlotLog.objects.create(plot=instance)


@receiver(post_save, weak=False, sender=PlotLogEntry, dispatch_uid="update_plot_on_post_save")
def update_plot_on_post_save(sender, instance, raw, created, using, **kwargs):
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


@receiver(post_delete, weak=False, sender=PlotLogEntry, dispatch_uid="update_plot_on_post_delete")
def update_plot_on_post_delete(instance, using, **kwargs):
    plot = Plot.objects.get(pk=instance.plot_log.plot.pk)
    try:
        PlotLogEntry.objects.get(plot_log__plot=plot)
    except PlotLogEntry.DoesNotExist:
        plot.accessible = True
    except MultipleObjectsReturned:
        pass
    plot.save()
