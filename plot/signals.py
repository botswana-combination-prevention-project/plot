# coding=utf-8

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Plot, PlotLog, PlotLogEntry
from plot.constants import INACCESSIBLE, ACCESSIBLE


@receiver(post_save, weak=False, sender=Plot, dispatch_uid="create_households_on_post_save")
def create_households_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        instance.create_or_delete_households()
        if created:
            PlotLog.objects.create(plot=instance)


@receiver(post_save, weak=False, sender=PlotLogEntry, dispatch_uid="update_plot_on_post_save")
def update_plot_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        plot = Plot.objects.get(pk=instance.plot_log.plot.pk)
        if instance.log_status == INACCESSIBLE:
            plot.accessible = False
            plot.gps_confirmed_latitude = None
            plot.gps_confirmed_longitude = None
            plot.distance_from_target = None
            plot.save()
        elif instance.log_status == ACCESSIBLE:
            plot.accessible = True
            plot.save()
