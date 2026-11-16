"""An offset after a reference wider than one day counts from its last day.

"the day after christmas" is 26 December: the offset counts from the day it
follows.  For a wider reference the same reading counts from its last day:
"two weeks after next summer" is two weeks after the summer ends, not two
weeks into it.  "before" counts back from the first day.

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
