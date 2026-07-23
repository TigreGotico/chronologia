"""ISO-8601 week references: "week 32", "week 32 of 2026".

ISO weeks are **Monday-based by the standard**, independent of any locale's
civil ``week_start`` convention: week 1 is the week containing the year's
first Thursday, and week N runs ``[Monday, next Monday)``.  Expected Mondays
are computed with the stdlib ``date.fromisocalendar`` -- independent of the
parser under test.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


# (text, iso-year, iso-week); the anchor year is 2017 when no year is named.
_CASES = [
    ("week 32", 2017, 32),
    ("week 1", 2017, 1),
    ("week 26", 2017, 26),
    ("week 52", 2017, 52),
    ("week 32 of 2026", 2026, 32),
    ("week 1 of 2026", 2026, 1),
    ("week 53 of 2020", 2020, 53),       # 2020 is a 53-week ISO year
    ("week 10 of 1999", 1999, 10),
    ("week 40 of 2024", 2024, 40),
    ("week 7 of 2030", 2030, 7),
    # the ordinal prose surface names the same week as the cardinal one
    ("the 10th week of 2024", 2024, 10),
    ("the 32nd week of 2026", 2026, 32),
    ("the 53rd week of 2020", 2020, 53),
    ("the tenth week of 2024", 2024, 10),
    ("the 1st week of 2026", 2026, 1),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    monday = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(monday.year, monday.month, monday.day)
    nxt = monday + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


# adversarial: a week number naming no ISO week in the year does not fire;
# 2017 has only 52 ISO weeks, so "week 53" (no year) is out of range.
@pytest.mark.parametrize("text", [
    "week 0", "week 60", "week 99 of 2020", "week 53",
    # an in-shape ordinal naming no ISO week refuses just like the cardinal
    "the 53rd week of 2024", "the 99th week of 2024",
])
def test_not_an_iso_week(text):
    nomatch(text)
