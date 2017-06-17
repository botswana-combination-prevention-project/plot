from django.core.management.base import BaseCommand, CommandError

from ...models import Plot
from django.db.utils import IntegrityError


def create_ess_plots(points, map_area):
    """Create plot instances.

        points: List of list, e.g [[latitude, longitude], [latitude, longitude]]
        map_area: Name of map location, e.g test_community.
    """
    number_of_points = 0
    for point in points:
        latitude = point[0]
        longitude = point[1]
        number_of_points += 1
        try:
            Plot.objects.create(
                gps_target_lat=latitude,
                gps_target_lon=longitude,
                map_area=map_area,
                ess=True)
            print(number_of_points, "number of plots created")
        except IntegrityError:
            pass


class Command(BaseCommand):

    args = (
        '<community name e.g otse>, file path e.g /Users/django/source/bcpp/plots.csv')
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        fname = (
            '/Users/django/source/pair9/plot_list_metsimotlhabe_75pct_update_201504011622.csv')
        map_area = 'test_community'
        f = open(fname, 'r')
        data = f.readlines()
        data.pop(0)
        points = []
        for point in data:
            point = point.strip().split(',')
            points.append([float(point[1]), float(point[2])])
        create_ess_plots(points, map_area)
        self.stdout.write(self.style.SUCCESS('Succefully created plots.'))
