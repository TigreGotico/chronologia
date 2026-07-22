"""Fuzzy sub-spans of a calendar period: "the beginning of the month",
"early next week", "the end of the year".

**Convention (documented, consistent across every scale).** early / mid / late
name the first / middle / last *arithmetic third* of the parent calendar
period -- the identical rule ``month_fuzzy`` ("mid-july") and ``decade_ref``
("late 90s") already use, via :func:`chronologia.subdivide`.  "beginning" and
"start" are synonyms for early; "middle" for mid; "end" for late.  The basis
stays exact and the width is honest: a 7-day week thirds into 2d8h slices, so
the boundaries fall mid-day -- and the test asserts those exact instants.

The parent period is the calendar container the UNIT names -- the anchor's
current week / month / year, or the one a relative marker shifts to.  Parent
edges below are hand-derived (anchor 2017-06-27, a Tuesday; Monday-start week);
the expected third is pure ``timedelta`` arithmetic over those edges, never the
parser.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch


def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second,
                    a.microsecond)


def _third(s, e, part):
    """The early/mid/late arithmetic third of the parent span ``[s, e)``."""
    s, e = _dt(s), _dt(e)
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
             "late": (s + 2 * w, e)}[part]
    return (AstroDate.from_datetime(edges[0]),
            AstroDate.from_datetime(edges[1]))


# parent calendar containers, hand-derived from the anchor.
_MONTH = (AstroDate(2017, 6, 1), AstroDate(2017, 7, 1))
_THIS_WEEK = (AstroDate(2017, 6, 26), AstroDate(2017, 7, 3))
_NEXT_WEEK = (AstroDate(2017, 7, 3), AstroDate(2017, 7, 10))
_LAST_WEEK = (AstroDate(2017, 6, 19), AstroDate(2017, 6, 26))
_THIS_YEAR = (AstroDate(2017, 1, 1), AstroDate(2018, 1, 1))

# (text, parent, part)
_CASES = [
    ("the beginning of the month", _MONTH, "early"),
    ("the start of the month", _MONTH, "early"),
    ("the middle of the month", _MONTH, "mid"),
    ("the end of the month", _MONTH, "late"),
    ("early next week", _NEXT_WEEK, "early"),
    ("the middle of next week", _NEXT_WEEK, "mid"),
    ("late next week", _NEXT_WEEK, "late"),
    ("early last week", _LAST_WEEK, "early"),
    ("the beginning of the year", _THIS_YEAR, "early"),
    ("the end of the year", _THIS_YEAR, "late"),
    ("the middle of the year", _THIS_YEAR, "mid"),
]


@pytest.mark.parametrize("text,parent,part", _CASES)
def test_fuzzy_period(text, parent, part):
    want_s, want_e = _third(parent[0], parent[1], part)
    s, e = start_end(text)
    assert s == want_s
    assert e == want_e


# adversarial: "early bird" is not a date; a bare period word without a UNIT
# does not fire.
@pytest.mark.parametrize("text", ["early bird", "the beginning", "end of days"])
def test_not_a_fuzzy_period(text):
    nomatch(text)
