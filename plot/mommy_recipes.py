# coding=utf-8

from geopy import Point
from random import random
from faker import Faker
from faker.providers import BaseProvider
from model_mommy.recipe import Recipe

from edc_base.utils import get_utcnow

from .models import Plot, PlotLogEntry, PlotLog


class GpsProvider(BaseProvider):

    target_point = Point(-25.330451, 25.556502)

    def target_latitude(self):
        return round(self.target_point.latitude - random() / 10000000, 15)

    def target_longitude(self):
        return round(self.target_point.longitude - random() / 10000000, 15)

    def confirmed_latitude(self):
        return round(self.target_point.latitude - random() / 10000000, 15)

    def confirmed_longitude(self):
        return round(self.target_point.longitude - random() / 10000000, 15)


fake = Faker()
fake.add_provider(GpsProvider)


plot = Recipe(
    Plot,
    report_datetime=get_utcnow,
    map_area='test_community',
    household_count=0,
    status=None,
    eligible_members=0,
    selected=None,
    gps_target_lat=fake.target_latitude,
    gps_target_lon=fake.target_longitude,
    ess=False,
    rss=False,
    htc=False,
)


plotlog = Recipe(
    PlotLog,
)


plotlogentry = Recipe(
    PlotLogEntry,
    report_datetime=get_utcnow,
)
