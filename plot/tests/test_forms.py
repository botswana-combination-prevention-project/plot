from django.test import TestCase, tag
from model_mommy import mommy

from ..forms import PlotForm, PlotLogForm, PlotLogEntryForm
from ..models import PlotLog

from .mixins import PlotMixin


class TestForms(PlotMixin, TestCase):

    def test_plot_form(self):
        plot = mommy.prepare_recipe('plot.plot')
        form = PlotForm(data=plot.__dict__)
        form.is_valid()
        print(form.errors)
        self.assertTrue(form.is_valid())

#     @tag('me')
#     def test_plot_log_form(self):
#         plot = self.make_confirmed_plot(household_count=1)
#         plot_log = PlotLog.objects.get(plot=plot)
#         # can only edit, never create
#         form = PlotLogForm(instance=plot_log)
#         form.is_valid()
#         print(form.errors)
#         print(form.non_field_errors())
#         self.assertTrue(form.is_valid())
# 
#     def test_plot_log_entry_form(self):
#         plot = self.make_confirmed_plot(household_count=1)
#         plot_log = PlotLog.objects.get(plot=plot)
#         plot_log_entry = mommy.prepare_recipe(
#             'plot.plotlogentry',
#             plot_log=plot_log,
#             report_datetime=self.get_utcnow())
#         form = PlotLogEntryForm(data=plot_log_entry.__dict__)
#         form.is_valid()
#         print(form.errors)
#         self.assertTrue(form.is_valid())
