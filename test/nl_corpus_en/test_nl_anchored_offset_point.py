"""Anchored 'N <period> after/before <anchor>' resolves to the shifted DAY.

"a week after christmas" means the single civil day one week after christmas
(2018-01-01), NOT a week-long span.  The offset amount governs the SHIFT; the
result is always one civil day wide, for every unit (day/week/month/year) --
exactly like an ordinary calendar day.

Regression guard for the silent-wrong where WEEK/MONTH/YEAR offsets returned a
period-wide span (the offset amount reused as the span width) while DAY offsets
were already a point.

Anchor 2017-06-27 (Tue, 13:04).  Reference days from the civil/computus table:

    christmas = Mon 2017-12-25   new year's day = 2018-01-01
    halloween = 2017-10-31       thanksgiving   = Thu 2017-11-23
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start

CHRISTMAS = date(2017, 12, 25)
NEW_YEAR = date(2018, 1, 1)
HALLOWEEN = date(2017, 10, 31)
THANKSGIVING = date(2017, 11, 23)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


# -- the shifted day is correct AND a single civil day wide ----------------

@pytest.mark.parametrize("text,expected", [
    ("a week after christmas", NEW_YEAR),               # +7 -> 2018-01-01
    ("a week before halloween", HALLOWEEN - timedelta(days=7)),
    ("a week after thanksgiving", THANKSGIVING + timedelta(days=7)),
    ("2 weeks after christmas", CHRISTMAS + timedelta(days=14)),
    ("1 month after christmas", date(2018, 1, 25)),
    ("two days before christmas", CHRISTMAS - timedelta(days=2)),
    ("3 days after christmas", CHRISTMAS + timedelta(days=3)),
])
def test_offset_resolves_to_single_shifted_day(text, expected):
    assert start(text) == _ad(expected)
    assert span(text).width == timedelta(days=1)
