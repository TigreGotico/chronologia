"""Calendar quarters: "Q3 2026", "the third quarter", "next quarter".

Quarter N (1..4) is the three calendar months ``[3N-2 .. 3N]``; the span runs
from the first day of its first month to the first day of the month after its
last.  A relative marker shifts by whole quarters from the anchor's current
one (the anchor is 2017-06-27, in Q2).  Expected edges are hand-derived.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, start_end, nomatch


# (text, first month's year, first month, month-after-last year, month)
_CASES = [
    ("Q3 2026", 2026, 7, 2026, 10),
    ("Q1 2020", 2020, 1, 2020, 4),
    ("Q4 2019", 2019, 10, 2020, 1),
    ("the third quarter of 2026", 2026, 7, 2026, 10),
    ("the first quarter of 2020", 2020, 1, 2020, 4),
    ("the fourth quarter of 2019", 2019, 10, 2020, 1),
    ("the third quarter", 2017, 7, 2017, 10),        # anchor year 2017
    ("the first quarter", 2017, 1, 2017, 4),
    ("the fourth quarter", 2017, 10, 2018, 1),
    ("this quarter", 2017, 4, 2017, 7),              # anchor is in Q2
    ("next quarter", 2017, 7, 2017, 10),             # Q2 -> Q3
    ("last quarter", 2017, 1, 2017, 4),              # Q2 -> Q1
    ("second quarter 2018", 2018, 4, 2018, 7),
]


@pytest.mark.parametrize("text,sy,sm,ey,em", _CASES)
def test_quarter(text, sy, sm, ey, em):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, 1)
    assert e == AstroDate(ey, em, 1)


# adversarial: a quarter outside 1..4 is no quarter; "a quarter of an hour"
# stays a duration (not a calendar quarter); a lone "quarter" without an
# ordinal is not a quarter reference.
@pytest.mark.parametrize("text", [
    "Q5 2026", "the fifth quarter", "the zeroth quarter",
    "a quarter of an hour", "quarter past nine",
])
def test_not_a_quarter(text):
    r = __import__("chronologia").extract_timespan(text, "en", ANCHOR)
    # either no parse at all, or it resolved to something that is NOT a
    # whole-quarter span (three calendar months starting on a quarter month)
    if r is not None:
        s, e = r[0].start, r[0].end
        assert not (s.day == 1 and s.month in (1, 4, 7, 10)
                    and (e.year - s.year) * 12 + (e.month - s.month) == 3)
