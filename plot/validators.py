from edc_map.site_mappers import site_mappers
from django.core.exceptions import ValidationError


def is_valid_community(value):
    """Validates the community string against a list of site_mappers map_areas."""
    if value.lower() not in [l.lower() for l in site_mappers.map_areas]:
        raise ValidationError(u'{0} is not a valid community name.'.format(value))
