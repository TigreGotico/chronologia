"""Impossible calendar dates must return None, never a fabricated span.

The never-fabricate contract PR #305 pinned for English is language-agnostic
calendar arithmetic and must hold in German too: a bare out-of-range day glued
to a month ("32. April") must not fall back to the whole month with the day
dropped.  Every VALID neighbour is pinned so the veto cannot over-fire.
"""
import pytest

from ._corpus import ANCHOR, nomatch, span
from chronologia.astrodate import AstroDate


@pytest.mark.parametrize("text", [
    "32. April",              # no day 32 in any month
    "31. April",              # April has 30 days
    "30. Februar",            # February never has 30 days
    "29. Februar 2017",       # 2017 is not a leap year
])
def test_impossible_day_vetoed_to_none(text):
    nomatch(text)


def test_thirty_april_resolves():
    assert span("30. April").start == AstroDate(2018, 4, 30)


def test_leap_day_2020_resolves():
    assert span("29. Februar 2020").start == AstroDate(2020, 2, 29)


def test_twenty_eight_februar_resolves():
    assert span("28. Februar").start == AstroDate(2018, 2, 28)
