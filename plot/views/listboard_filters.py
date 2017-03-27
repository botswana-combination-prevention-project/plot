from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters


class PlotListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        position=0,
        label='All',
        lookup={})

    accessible = ListboardFilter(
        name='accessible',
        position=10,
        label='Accessible',
        lookup={'accessible': True})

    ess = ListboardFilter(
        label='ESS',
        position=20,
        lookup={'ess': True})

    rss = ListboardFilter(
        label='RSS',
        position=30,
        lookup={'rss': True})

    htc = ListboardFilter(
        label='HTC',
        position=40,
        lookup={'htc': True})

    enrolled = ListboardFilter(
        label='Enrolled',
        position=50,
        lookup={'enrolled': True})

    not_enrolled = ListboardFilter(
        label='Not enrolled',
        position=60,
        lookup={'enrolled': False})

    enrolled80 = ListboardFilter(
        label='Enrolled (from 80%)',
        position=65,
        lookup={'enrolled': True, 'selected__isnull': True})

    confirmed = ListboardFilter(
        label='Confirmed',
        position=70,
        lookup={'confirmed': True})

    not_confirmed = ListboardFilter(
        label='Not confirmed',
        position=80,
        lookup={'confirmed': False})

    attempts_0 = ListboardFilter(
        label='Attempts (0)',
        position=90,
        lookup={'access_attempts': 0})

    attempts_gte_0 = ListboardFilter(
        label='Attempts (>0)',
        position=100,
        lookup={'access_attempts__gte': 1})

    attempts_1 = ListboardFilter(
        label='Attempts (1)',
        position=110,
        lookup={'access_attempts': 1})

    attempts_2 = ListboardFilter(
        label='Attempts (2)',
        position=120,
        lookup={'access_attempts': 2})

    attempts_3 = ListboardFilter(
        label='Attempts (>=3)',
        position=130,
        lookup={'access_attempts__gte': 3})
