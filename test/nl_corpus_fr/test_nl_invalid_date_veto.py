"""Impossible calendar dates must return None, never a fabricated span.

The never-fabricate contract PR #305 pinned for English is language-agnostic
calendar arithmetic and must hold in French too: a bare out-of-range day glued
to a month ("32 avril") must not fall back to the whole month with the day
dropped.  Every VALID neighbour is pinned so the veto cannot over-fire.
"""
import pytest

from ._corpus import ANCHOR, nomatch, span
from chronologia.astrodate import AstroDate


@pytest.mark.parametrize("text", [
    "32 avril",               # no day 32 in any month
    "31 avril",               # April has 30 days
    "30 février",             # February never has 30 days
    "29 février 2017",        # 2017 is not a leap year
])
def test_impossible_day_vetoed_to_none(text):
    nomatch(text)


def test_thirty_avril_resolves():
    assert span("30 avril").start == AstroDate(2018, 4, 30)


def test_leap_day_2020_resolves():
    assert span("29 février 2020").start == AstroDate(2020, 2, 29)


def test_twenty_eight_fevrier_resolves():
    assert span("28 février").start == AstroDate(2018, 2, 28)
