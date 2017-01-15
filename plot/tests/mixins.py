from edc_base_test.mixins.dates_test_mixin import DatesTestMixin

from .plot_test_mixin import PlotTestMixin


class PlotMixin(PlotTestMixin, DatesTestMixin):

    """A local mixin for the plot module."""
    pass
