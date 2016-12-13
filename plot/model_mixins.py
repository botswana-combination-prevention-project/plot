from django.db import models
from edc_map.site_mappers import site_mappers
from edc_map.exceptions import MapperError


class GpsModelMixin(models.Model):

    gps_degrees_s = models.DecimalField(
        verbose_name='GPS Degrees-South',
        max_digits=10,
        null=True,
        decimal_places=0)

    gps_minutes_s = models.DecimalField(
        verbose_name='GPS Minutes-South',
        max_digits=10,
        null=True,
        decimal_places=4)

    gps_degrees_e = models.DecimalField(
        verbose_name='GPS Degrees-East',
        null=True,
        max_digits=10,
        decimal_places=0)

    gps_minutes_e = models.DecimalField(
        verbose_name='GPS Minutes-East',
        max_digits=10,
        null=True,
        decimal_places=4)

    gps_lon = models.DecimalField(
        verbose_name='longitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_lat = models.DecimalField(
        verbose_name='latitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_target_lon = models.DecimalField(
        verbose_name='target waypoint longitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    gps_target_lat = models.DecimalField(
        verbose_name='target waypoint latitude',
        max_digits=10,
        null=True,
        decimal_places=6,
        editable=False)

    def save(self, *args, **kwargs):
        # if user added/updated gps_degrees_[es] and gps_minutes_[es], update gps_lat, gps_lon
        if (self.gps_degrees_e and self.gps_degrees_s and self.gps_minutes_e and self.gps_minutes_s):
            mapper = site_mappers.get_mapper(site_mappers.current_map_area)
            self.gps_lat = mapper.get_gps_lat(self.gps_degrees_s, self.gps_minutes_s)
            self.gps_lon = mapper.get_gps_lon(self.gps_degrees_e, self.gps_minutes_e)
            mapper.verify_gps_location(self.gps_lat, self.gps_lon, MapperError)
            mapper.verify_gps_to_target(self.gps_lat, self.gps_lon, self.gps_target_lat,
                                        self.gps_target_lon, self.target_radius, MapperError,
                                        radius_bypass_instance=self.increase_radius_instance)
            self.distance_from_target = mapper.gps_distance_between_points(
                self.gps_lat, self.gps_lon, self.gps_target_lat, self.gps_target_lon) * 1000
        super(GpsModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
