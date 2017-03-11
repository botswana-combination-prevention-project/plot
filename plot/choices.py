# coding=utf-8

from .constants import (
    NON_RESIDENTIAL, RESIDENTIAL_NOT_HABITABLE, RESIDENTIAL_HABITABLE, INACCESSIBLE,
    TWENTY_PERCENT, FIVE_PERCENT, ACCESSIBLE)

PLOT_STATUS = (
    (NON_RESIDENTIAL, 'non-residential'),
    (RESIDENTIAL_NOT_HABITABLE, 'residential, not-habitable'),
    (RESIDENTIAL_HABITABLE, 'residential, habitable'),
    (INACCESSIBLE, 'Inaccessible'),
)

SELECTED = (
    (TWENTY_PERCENT, 'twenty_percent'),
    (FIVE_PERCENT, 'five_percent'),
)

PLOT_LOG_STATUS = (
    (ACCESSIBLE, 'Accessible'),
    (INACCESSIBLE, 'Inaccessible'),
)

INACCESSIBILITY_REASONS = (
    ('impassable_road', 'Road is impassable'),
    ('dogs', 'Dogs prevent access'),
    ('locked_gate', 'Gate is locked'),
    ('OTHER', 'Other'),
)
