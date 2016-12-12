from edc_identifier.alphanumeric_identifier import AlphanumericIdentifier


class PlotIdentifier(AlphanumericIdentifier):

    def __init__(self, community, using):
        identifier_format = '{community}{sequence}'
        app_name = 'bcpp_plot'
        model_name = 'plotidentifierhistory'
        modulus = 11
        self.set_community(community)
        super(PlotIdentifier, self).__init__(
            identifier_format=identifier_format,
            app_name=app_name,
            model_name=model_name,
            modulus=modulus,
            using=using)

    def set_community(self, value):
        if not value:
            raise TypeError('Attribute \'community\' may not be None for plot identifier')
        self._community = value

    def get_community(self):
        return self._community

    def get_identifier_prep(self, **kwargs):
        """ Users may override to pass non-default keyword arguments to get_identifier
        before the identifier is created."""
        return {'community': self.get_community()}
