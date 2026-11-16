""""after next" and "before last" end the idiom only at the end of the phrase.

"the day after next" is the day after tomorrow, and "the day before last" the
day before yesterday.  When a season, month, weekday or holiday follows the
marker, the marker belongs to that reference: "the day after next summer" is
the day after next summer, not the day after tomorrow with "summer" left
over.  The offset counts from the last day of the reference, so it is 1
September 2027 (meteorological summer is June, July and August: NOAA NCEI,
"Meteorological Versus Astronomical Seasons").

16 November 2026 is a Monday.  The gold is date arithmetic and
``dateutil.easter``, never read back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import parse

ANCHOR = datetime(2026, 11, 16, 12, 0)
TODAY = ANCHOR.date()
NEXT_MONDAY = TODAY + timedelta(weeks=1)
LAST_DAY_OF_NEXT_SUMMER = date(2027, 8, 31)


def _first_monday_after(day):
    return day + timedelta(days=7 - day.weekday())


@pytest.mark.parametrize("text, day, remainder", [
    ("remind me the day after next summer",
     LAST_DAY_OF_NEXT_SUMMER + timedelta(days=1), "remind me"),
    ("the day after next monday", NEXT_MONDAY + timedelta(days=1), ""),
    ("the day before last christmas", date(2025, 12, 24), ""),
    ("the day after next easter", easter(2027) + timedelta(days=1), ""),
    ("the monday after next summer",
     _first_monday_after(LAST_DAY_OF_NEXT_SUMMER), ""),
])
def test_the_marker_belongs_to_the_reference_after_it(text, day, remainder):
    span, rest = parse(text, ANCHOR)
    assert (span.start.year, span.start.month, span.start.day) == (
        day.year, day.month, day.day)
    assert span.end - span.start == timedelta(days=1)
    assert rest == remainder


@pytest.mark.parametrize("text, day", [
    # controls: the idiom alone
    ("the day after next", TODAY + timedelta(days=2)),
    ("the day before last", TODAY - timedelta(days=2)),
    ("the monday after next", NEXT_MONDAY + timedelta(weeks=1)),
])
def test_the_idiom_at_the_end_of_the_phrase_is_unchanged(text, day):
    span, rest = parse(text, ANCHOR)
    assert (span.start.year, span.start.month, span.start.day) == (
        day.year, day.month, day.day)
    assert rest == ""
