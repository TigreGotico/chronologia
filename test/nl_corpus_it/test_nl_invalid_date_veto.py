"""Impossible calendar dates must return None, never a fabricated span.

The same never-fabricate contract PR #305 pinned for English (a day that
cannot exist is vetoed to ``None`` rather than silently widened to the
whole month) is language-agnostic calendar arithmetic and must hold in
Italian too.  A bare out-of-range day glued to a month ("32 aprile") must
not fall back to the whole month with the day dropped.

Every VALID neighbour is pinned alongside so the veto cannot over-fire.
"""
import pytest

from ._corpus import ANCHOR, nomatch, span
from chronologia.astrodate import AstroDate


@pytest.mark.parametrize("text", [
    "32 aprile",              # no day 32 in any month
    "31 aprile",              # April has 30 days
    "30 febbraio",            # February never has 30 days
    "29 febbraio 2017",       # 2017 is not a leap year
])
def test_impossible_day_vetoed_to_none(text):
    nomatch(text)


# -- valid neighbours the veto must NOT swallow (regression pins) ---------
def test_thirty_aprile_resolves():
    assert span("30 aprile").start == AstroDate(2018, 4, 30)


def test_leap_day_2020_resolves():
    assert span("29 febbraio 2020").start == AstroDate(2020, 2, 29)


def test_twenty_eight_febbraio_resolves():
    assert span("28 febbraio").start == AstroDate(2018, 2, 28)
