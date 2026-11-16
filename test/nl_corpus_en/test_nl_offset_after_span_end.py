"""An offset after a reference counts from its last day when its unit is
shorter than the reference.

"two weeks after next summer" is two weeks after the summer ends, not two
weeks into it: a week is shorter than a season.  A unit as long as the
reference or longer counts unit by unit from its first day: "2 years after
1990" is 1992, and "a month after march" is April.  "before" counts back from
the first day.

Season bounds are meteorological, as ``chronologia.extract.ranges`` reads
them. NOAA NCEI, "Meteorological Versus Astronomical Seasons":
"meteorological summer includes June, July, and August" (northern
hemisphere).  So at 16 November 2026, "next summer" is 1 June to 31 August
2027.

The gold is computed with date arithmetic, never read back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)
LAST_DAY_OF_NEXT_SUMMER = date(2027, 8, 31)
FIRST_DAY_OF_NEXT_SUMMER = date(2027, 6, 1)


def _day(text):
    got = parse(text, ANCHOR)
    assert got is not None, text
    span, remainder = got
    s = span.start
    assert span.end - span.start == timedelta(days=1)
    return date(s.year, s.month, s.day), remainder


@pytest.mark.parametrize("text, day, remainder", [
    ("remind me two weeks after next summer",
     LAST_DAY_OF_NEXT_SUMMER + timedelta(weeks=2), "remind me"),
    ("one month after next summer",
     LAST_DAY_OF_NEXT_SUMMER + relativedelta(months=1), ""),
    ("the invoice is due three days after june 2027",
     date(2027, 6, 30) + timedelta(days=3), "the invoice is due"),
    # bare "the summer" at the anchor is the summer of 2026
    ("the shop opens a week after the summer",
     date(2026, 8, 31) + timedelta(weeks=1), "the shop opens"),
    ("we move 3 months after summer",
     date(2026, 8, 31) + relativedelta(months=3), "we move"),
    # bare "march" at the anchor is March 2026
    ("the report is due a week after march",
     date(2026, 3, 31) + timedelta(weeks=1), "the report is due"),
    # a weekday has no unit: the first monday after 30 June 2027, a Wednesday
    ("the monday after june 2027",
     date(2027, 6, 30) + timedelta(days=(0 - date(2027, 6, 30).weekday()) % 7),
     ""),
])
def test_after_a_span_counts_from_its_last_day(text, day, remainder):
    assert _day(text) == (day, remainder)


@pytest.mark.parametrize("text, day, remainder", [
    # controls: "before" counts from the first day, and a one-day
    # reference has one day to count from
    ("we leave two weeks before next summer",
     FIRST_DAY_OF_NEXT_SUMMER - timedelta(weeks=2), "we leave"),
    ("two days after christmas", date(2026, 12, 27), ""),
    ("a week after june 1st", date(2027, 6, 8), ""),
])
def test_before_a_span_and_after_a_day_are_unchanged(text, day, remainder):
    assert _day(text) == (day, remainder)


@pytest.mark.parametrize("text, day, remainder", [
    # a unit as long as the reference counts unit by unit from its first day
    ("the lease ends a month after march",
     date(2026, 3, 1) + relativedelta(months=1), "the lease ends"),
    ("2 years after 1990", date(1990, 1, 1) + relativedelta(years=2), ""),
    ("a year after next summer",
     FIRST_DAY_OF_NEXT_SUMMER + relativedelta(years=1), ""),
])
def test_a_unit_as_long_as_the_reference_counts_from_its_start(
        text, day, remainder):
    assert _day(text) == (day, remainder)

