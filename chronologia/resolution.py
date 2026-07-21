"""Temporal granularity enumeration.

``DateTimeResolution`` names the granularity ("width") of a temporal
reference: a day, a week, a month, a year, a decade, a century, a
millennium, or a count backwards from the before-present epoch.

In chronologia the resolution is *derived*, never asserted: a
:class:`~chronologia.astrodate.DateSpan` computes its own resolution from
the width of its half-open interval. This enum is the vocabulary that
derivation reports.

Provenance: extracted verbatim (enum members and their integer values
unchanged) from ``ovos_date_parser.ranges``. Only the closed set of
members needed by the reckoning core is vendored here; the surrounding
range/season utilities of that module deliberately stay behind, as they
carry parser-only dependencies.
"""
from enum import Enum


class DateTimeResolution(Enum):
    """Granularity of a temporal reference.

    ``UNIT`` counts from the start of the calendar (ordinal 1 = year 1);
    ``UNIT_OF_SCOPE`` counts inside the scope containing the reference
    date; ``BEFORE_PRESENT_UNIT`` counts backwards from the before-present
    reference epoch (January 1st 1950, as in radiocarbon dating).
    """
    DAY = 0
    DAY_OF_MONTH = 1
    DAY_OF_YEAR = 2
    DAY_OF_DECADE = 3
    DAY_OF_CENTURY = 4
    DAY_OF_MILLENNIUM = 5

    WEEK = 6
    WEEK_OF_MONTH = 7
    WEEK_OF_YEAR = 8
    WEEK_OF_DECADE = 9
    WEEK_OF_CENTURY = 10
    WEEK_OF_MILLENNIUM = 11

    MONTH = 12
    MONTH_OF_YEAR = 13
    MONTH_OF_DECADE = 14
    MONTH_OF_CENTURY = 15
    MONTH_OF_MILLENNIUM = 16

    YEAR = 17
    YEAR_OF_DECADE = 18
    YEAR_OF_CENTURY = 19
    YEAR_OF_MILLENNIUM = 20

    DECADE = 21
    DECADE_OF_CENTURY = 22
    DECADE_OF_MILLENNIUM = 23

    CENTURY = 24
    CENTURY_OF_MILLENNIUM = 25

    MILLENNIUM = 26

    BEFORE_PRESENT_DAY = 27
    BEFORE_PRESENT_WEEK = 28
    BEFORE_PRESENT_MONTH = 29
    BEFORE_PRESENT_YEAR = 30
    BEFORE_PRESENT_DECADE = 31
    BEFORE_PRESENT_CENTURY = 32
    BEFORE_PRESENT_MILLENNIUM = 33
