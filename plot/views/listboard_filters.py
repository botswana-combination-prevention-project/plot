from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class PlotListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        position=0,
        label='All',
        lookup={})

    accessible = ListboardFilter(
        name='accessible',
        position=1,
        label='Accessible',
        lookup={'accessible': True})

    ess = ListboardFilter(
        label='ESS',
        position=2,
        lookup={'ess': True})

    rss = ListboardFilter(
        label='RSS',
        position=3,
        lookup={'rss': True})

    htc = ListboardFilter(
        label='HTC',
        position=4,
        lookup={'htc': True})

    enrolled = ListboardFilter(
        label='Enrolled',
        position=5,
        lookup={'enrolled': True})

    not_enrolled = ListboardFilter(
        label='Not enrolled',
        position=6,
        lookup={'enrolled': False})

    confirmed = ListboardFilter(
        label='Confirmed',
        position=7,
        lookup={'confirmed': True})

    not_confirmed = ListboardFilter(
        label='Not confirmed',
        position=8,
        lookup={'confirmed': False})

    attempts_0 = ListboardFilter(
        label='Attempts (0)',
        position=9,
        lookup={'access_attempts': 0})

    attempts_1 = ListboardFilter(
        label='Attempts (>0)',
        position=10,
        lookup={'access_attempts__gte': 1})

    attempts_1 = ListboardFilter(
        label='Attempts (=>1)',
        position=11,
        lookup={'access_attempts__gte': 1})

    attempts_2 = ListboardFilter(
        label='Attempts (=>2)',
        position=12,
        lookup={'access_attempts__gte': 2})
