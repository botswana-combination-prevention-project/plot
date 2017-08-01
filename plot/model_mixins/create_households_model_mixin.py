# coding=utf-8

from django.apps import apps as django_apps
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import options
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

if 'household_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('household_model',)


class CreateHouseholdError(Exception):
    pass


class MaxHouseholdsExceededError(Exception):
    pass


class CreateHouseholdsModelMixin(models.Model):

    household_count = models.IntegerField(
        verbose_name="Number of Households on this plot.",
        default=0,
        validators=[MaxValueValidator(9)],
        help_text=("Provide the number of households in this plot."))

    def common_clean(self):
        if not (self.gps_confirmed_longitude and self.gps_confirmed_latitude):
            if self.household_count > 0:
                raise CreateHouseholdError(
                    f'Households cannot exist on a unconfirmed plot. '
                    f'Got household count = {self.household_count}. Perhaps '
                    f'add the confirmation GPS point.')

            if self.eligible_members:
                raise CreateHouseholdError(
                    'Households cannot exist on a unconfirmed plot. '
                    'Got eligible_members eligible_members = '
                    f'{self.eligible_members}')
        super().common_clean()

    @property
    def common_clean_exceptions(self):
        return super().common_clean_exceptions + [
            CreateHouseholdError, MaxHouseholdsExceededError]

    def create_or_delete_households(self):
        """Creates or deletes households to try to equal the
        household_count.

        Delete will fail if household has data upstream.
        """
        app_config = django_apps.get_app_config('plot')

        if self.household_count > app_config.max_households:
            raise MaxHouseholdsExceededError(
                f'Number of households per plot cannot exceed '
                f'{app_config.max_households}. See plot.AppConfig')

        if self.gps_confirmed_longitude and self.gps_confirmed_latitude:
            Household = django_apps.get_model(
                *self._meta.household_model.split('.'))
            households = Household.objects.filter(plot=self)
            to_delete = households.count() - self.household_count

            if to_delete > 0:
                for household in households:
                    self.safe_delete(household)
                    to_delete -= 1
                    if not to_delete:
                        break
            elif households.count() < self.household_count:
                self.create_households()

            self.household_count = Household.objects.filter(
                plot__id=self.id).count()
            self.save(update_fields=['household_count'])

    def create_households(self):
        Household = django_apps.get_model(
            *self._meta.household_model.split('.'))
        for n in range(1, self.household_count + 1):
            with transaction.atomic():
                try:
                    Household.objects.create(
                        plot=self,
                        household_sequence=n,
                        report_datetime=self.report_datetime)
                except IntegrityError:
                    pass

    def safe_delete(self, household):
        """Safe delete households passing on ProtectedErrors.
        """
        HouseholdLog = django_apps.get_model('household.householdlog')
        HouseholdStructure = django_apps.get_model(
            'household.householdstructure')
        household_structures = HouseholdStructure.objects.filter(
            household=household)
        for household_structure in household_structures:
            try:
                for household_log in HouseholdLog.objects.filter(
                        household_structure=household_structure):
                    household_log.delete()
                    household_structure.delete()
                    household.delete()
            except ProtectedError:
                pass

    class Meta:
        abstract = True
        household_model = None
