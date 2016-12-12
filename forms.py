from django import forms

from edc_map.site_mappers import site_mappers

from .models import Plot, PlotLog


class PlotForm(forms.ModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data

        if self.instance.plot_identifier == site_mappers.get_mapper(
                site_mappers.current_map_area).clinic_plot_identifier:
            raise forms.ValidationError('Plot is a special plot that represents the BCPP Clinic. '
                                        'It may not be edited by a user.')
        try:
            self.instance.allow_enrollment('default',
                                           plot_instance=Plot(**cleaned_data),
                                           exception_cls=forms.ValidationError)
        except AttributeError:
            raise forms.ValidationError('System settings do not allow for this form to be '
                                        'edited. (e.g. mapper, community, site_code, device)')
        if self.instance.replaced_by:
            raise forms.ValidationError('Plot has been replaced and is not longer a BHS plot. '
                                        '(replaced_by={}'.format(self.instance.replaced_by))
        if self.instance.htc:
            raise forms.ValidationError('Plot is not a BHS plot (htc=True).')
        if not self.instance.community:
            raise forms.ValidationError('Community may not be blank. Must be '
                                        'one of {1}.'.format(self.instance.community,
                                                             ', '.join(site_mappers.get_as_list())))
        if self.instance.community not in site_mappers.get_as_list():
            raise forms.ValidationError('Unknown community {0}. Must be one '
                                        'of {1}.'.format(self.instance.community,
                                                         ', '.join(site_mappers.get_as_list())))
        if not self.instance.validate_plot_accessible:
            raise forms.ValidationError('You cannot confirm a plot, plot log entry is set to inacccessible.')

        if not (cleaned_data.get('household_count') and cleaned_data.get('status') in ['residential_habitable']):
            raise forms.ValidationError(
                'Invalid number of households. Only plots that are residential habitable can have households.')

        self.household_count_and_status(cleaned_data)
        self.status_and_eligible_member(cleaned_data)
        self.gps_coordinates_filled(cleaned_data)
        self.gps_verification(cleaned_data)
        self.complete_plot_log_entry(cleaned_data)
        self.best_time_to_visit(cleaned_data)

        return cleaned_data

    def household_count_and_status(self, cleaned_data):
        """Check if a residential_habitable plot has a household count greater than zero."""

        if (cleaned_data.get('household_count') == 0 and
                cleaned_data.get('status') in ['residential_habitable']) or (
                    cleaned_data.get('household_count') and not
                    cleaned_data.get('status') in ['residential_habitable']):
            raise forms.ValidationError('Invalid number of households for plot that is '
                                        '{0}. Got {1}.'.format(cleaned_data.get('status'),
                                                               cleaned_data.get('household_count')))

    def status_and_eligible_member(self, cleaned_data):
        """Check if the plot status is not residential_habitable number of eligible member is 0."""

        if not cleaned_data.get('status') == 'residential_habitable' and cleaned_data.get('eligible_members') > 0:
            raise forms.ValidationError('If the residence is not residential_habitable, '
                                        'number of eligible members should be 0. Got '
                                        '{0}'.format(cleaned_data.get('eligible_members')))

    def gps_coordinates_filled(self, cleaned_data):
        """Check of gps verification coordinates g=have been filled."""

        if (not cleaned_data.get('gps_degrees_s') and not cleaned_data.get('gps_minutes_s') and
                not cleaned_data.get('gps_degrees_e') and not cleaned_data.get('gps_minutes_e')):
            raise forms.ValidationError('The following fields must all be filled '
                                        'gps_degrees_s, gps_minutes_s, gps_degrees_e, '
                                        'gps_minutes_e. Got {0}, {1}, {2}, '
                                        '{3}'.format(cleaned_data.get('gps_degrees_s'),
                                                     cleaned_data.get('gps_minutes_s'),
                                                     cleaned_data.get('gps_degrees_e'),
                                                     cleaned_data.get('gps_minutes_e')))

    def gps_verification(self, cleaned_data):
        """Verify gps target location and check within community radius."""

        mapper_cls = site_mappers.registry.get(self.instance.community)
        mapper = mapper_cls()
        self.instance.verify_plot_community_with_current_mapper(
            self.instance.community, exception_cls=forms.ValidationError)
        gps_lat = mapper.get_gps_lat(cleaned_data.get('gps_degrees_s'), cleaned_data.get('gps_minutes_s'))
        gps_lon = mapper.get_gps_lon(cleaned_data.get('gps_degrees_e'), cleaned_data.get('gps_minutes_e'))
        mapper.verify_gps_location(gps_lat, gps_lon, forms.ValidationError)
        mapper.verify_gps_to_target(gps_lat, gps_lon, self.instance.gps_target_lat,
                                    self.instance.gps_target_lon, self.instance.target_radius,
                                    forms.ValidationError)

    def complete_plot_log_entry(self, cleaned_data):
        """Check if a plot log entry has been created before confirming a plot."""

        if (cleaned_data.get('gps_degrees_s') and
                cleaned_data.get('gps_minutes_s') and
                cleaned_data.get('gps_degrees_e') and
                cleaned_data.get('gps_minutes_e')):
            try:
                PlotLog.objects.get(plot=self.instance)
            except PlotLog.DoesNotExist:
                raise forms.ValidationError(
                    'Please add a plot log entry before saving')

    def best_time_to_visit(self, cleaned_data):
        """Raise an error if time of the day is specified if residence is NOT residential_habitable or not specific
         if residential_habitable.
         """

        if not cleaned_data.get('status') == 'residential_habitable' and (
                cleaned_data.get('time_of_week') or cleaned_data.get('time_of_day')):
            raise forms.ValidationError('If the residence is NOT residential_habitable, '
                                        'do not provide the best time to visit (e.g time of week, time of day).')
        if cleaned_data.get('status') == 'residential_habitable' and (
                not cleaned_data.get('time_of_week') or not cleaned_data.get('time_of_day')):
            raise forms.ValidationError('If the residence is residential_habitable, provide '
                                        'the best time to visit (e.g time of week, time of day).')

    class Meta:
        model = Plot
        fields = '__all__'
