# coding=utf-8

from django.db import models

from ..choices import SELECTED
from ..constants import TWENTY_PERCENT, FIVE_PERCENT


class PlotCreateError(Exception):
    pass


class PlotEnrollmentError(Exception):
    pass


class PlotEnrollmentMixin(models.Model):

    htc = models.BooleanField(
        default=False,
        editable=False)

    ess = models.BooleanField(
        default=False,
        blank=True,
        help_text=('True if plot is part of ESS and outside of '
                   'plots randomly selected'))

    rss = models.BooleanField(
        editable=False,
        default=False,
        help_text=('True if plot is one of those randomly '
                   'selected. See plot.selected'))

    selected = models.CharField(
        max_length=25,
        verbose_name='selected',
        choices=SELECTED,
        editable=False,
        null=True,
        help_text=(
            '1=20% of selected plots, 2=additional 5% selected '
            'buffer/pool, None=75%'))

    enrolled = models.BooleanField(
        default=False,
        help_text=('True indicates that plot is enrolled into a survey. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    enrolled_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text=('datetime that plot is enrolled into BHS. '
                   'Updated by bcpp_subject.subject_consent post_save'))

    def common_clean(self):
        if self.htc and self.selected in [TWENTY_PERCENT, FIVE_PERCENT]:
            if self.enrolled:
                raise PlotEnrollmentError(
                    'Plot cannot be enrolled. Plot cannot be assigned '
                    'to both HTC and RSS.')
            else:
                raise PlotCreateError(
                    'Plot cannot be assigned to both HTC and RSS.')
        if self.ess and any([self.htc, self.rss, self.selected]):
            raise PlotEnrollmentError(
                'Plot cannot be an ESS plot. Check value of RSS, HTC '
                'or \'selected\'.')
        if self.htc and not self.ess and self.enrolled:
            raise PlotEnrollmentError(
                'Plot cannot be enrolled. Got plot is assigned to HTC.')
        if self.enrolled and not self.enrolled_datetime:
            raise PlotEnrollmentError(
                'Plot cannot be enrolled. Got '
                'plot requires an enrolled datetime.')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [
            PlotEnrollmentError, PlotCreateError]

    def save(self, *args, **kwargs):
        self.rss = True if self.selected in [
            TWENTY_PERCENT, FIVE_PERCENT] else False
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
