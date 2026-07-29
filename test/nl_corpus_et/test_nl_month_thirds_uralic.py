"""Month-thirds for a *named* month (et): "märtsi algus/keskpaik/lõpp"
(early/mid/late March) must narrow to the first/middle/last arithmetic
third of the calendar month -- not silently return the whole month and
strand the postposed third-marker (algus/keskpaik/lõpp).

Uralic word order is genitive MONTH-first, marker postposed
(märtsi + algus/keskpaik/lõpp), unlike the pre-posed Romance/Germanic
"early March".  Thirds are pure timedelta arithmetic over the hand-derived
month edges; the plain-month case is pinned as a regression guard.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, span, start_end

A = datetime(2017, 6, 27, 13, 4)

MAR = (AstroDate(2017, 3, 1), AstroDate(2017, 4, 1))


def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second,
                    a.microsecond)


def _third(edges, part):
    s, e = _dt(edges[0]), _dt(edges[1])
    w = (e - s) / 3
    lo, hi = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
              "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(lo), AstroDate.from_datetime(hi)


_CASES = [("märtsi algus", "early"), ("märtsi keskpaik", "mid"),
          ("märtsi lõpp", "late")]


@pytest.mark.parametrize("text,part", _CASES)
def test_month_thirds(text, part):
    want_s, want_e = _third(MAR, part)
    s, e = start_end(text, A)
    assert (s, e) == (want_s, want_e)


@pytest.mark.parametrize("text,part", _CASES)
def test_month_thirds_no_strand(text, part):
    r = parse(text, A)
    assert r is not None
    assert not r[1].strip(), f"{text!r} stranded leftover {r[1]!r}"


def test_plain_month_regression():
    """Plain "märts" (no third-marker) stays the WHOLE month."""
    s = span("märts", A)
    assert (s.start, s.end) == MAR
