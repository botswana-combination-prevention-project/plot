from edc_identifier.research_identifier import ResearchIdentifier


class PlotIdentifier(ResearchIdentifier):

    template = '{study_site}{sequence}'
    label = 'plot_identifier'
