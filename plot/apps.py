from django.apps.config import AppConfig as DjangoAppConfig
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import CLOSED, OPEN
from edc_device.constants import SERVER


class Enrollment:
    def __init__(self, opening_datetime, closing_datetime):
        self.opening_datetime = opening_datetime
        self.closing_datetime = closing_datetime

    @property
    def status(self, reference_datetime=None):
        reference_datetime = reference_datetime or get_utcnow()
        if self.closing_datetime < reference_datetime:
            status = CLOSED
        else:
            status = OPEN
        return status


class Permisions:
    def __init__(self, create_roles=None, create_devices=None):
        self.create_roles = create_roles
        self.create_devices = create_devices

    def add(self, value=None):
        add = False
        if value in self.create_roles + self.create_devices:
            add = True
        return add


class AppConfig(DjangoAppConfig):
    name = 'plot'
    enrollment = Enrollment(
        timezone.now() - relativedelta(years=1),
        timezone.now() + relativedelta(years=1))
    max_households = 9
    permissions = Permisions(create_roles=[SERVER])
