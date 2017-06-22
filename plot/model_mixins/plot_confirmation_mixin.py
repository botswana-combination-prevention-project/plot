# coding=utf-8

from django.apps import apps as django_apps
from django.db import models

from edc_map.exceptions import MapperError

from .plot_enrollment_model_mixin import PlotEnrollmentError


class PlotConfirmationError(Exception):
    pass


class PlotConfirmationMixin(models.Model):

    def common_clean(self):
        if not self.id:
            if (self.gps_confirmed_latitude or
                    self.gps_confirmed_longitude) and not self.ess:
                raise PlotConfirmationError(
                    'Blocking attempt to confirm non-ESS plot on add.')
        else:
            if self.gps_confirmed_latitude and self.gps_confirmed_longitude:
                self.get_confirmed()  # confirmation point is within the radius
                try:
                    PlotLog = django_apps.get_model(*'plot.plotlog'.split('.'))
                    PlotLog.objects.get(plot__pk=self.id)
                except PlotLog.DoesNotExist:
                    app_config = django_apps.get_app_config('plot')
                    if app_config.excluded_plot(self):
                        # excluded plots are not normal plots to
                        # be surveyed, dont allow confirmation
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. Got plot logs '
                            'are not created for excluded plots.')
                    else:
                        # add Plot -> signal creates PlotLog, -> user
                        # creates PlotLogEntry -> user may update Plot
                        raise PlotConfirmationError(
                            'Plot cannot be confirmed. '
                            'Got plot log not created.')
            try:
                self.get_confirmed()
            except MapperError:
                if self.enrolled:
                    # once enrolled, dont allow modification to GPS
                    raise PlotEnrollmentError(
                        'Plot cannot be unconfirmed. Got plot is '
                        'already enrolled.')
        return super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [PlotConfirmationError]

    class Meta:
        abstract = True
