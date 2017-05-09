from django.core.management.base import BaseCommand

from edc_map.site_mappers import site_mappers
from edc_map.models import InnerContainer


def update_anonymous_sectioning():
    inner_containers = InnerContainer.objects.filter(map_area=site_mappers.current_map_area)
    count = 0
    for inner_container in inner_containers:
        ano_plot_dentifier = site_mappers.current_map_code + inner_container.device_id + '00-00'
        inner_container.labels = inner_container.labels + ',' + ano_plot_dentifier
        inner_container.save()
        count += 1
        print(f'Succefully updated sectioning for {inner_container}', f'{count} completed')


class Command(BaseCommand):

    args = '<community name e.g otse>, file path e.g /Users/django/source/bcpp/plots.csv'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        update_anonymous_sectioning()
        self.stdout.write(self.style.SUCCESS('Succefully created plots.'))
