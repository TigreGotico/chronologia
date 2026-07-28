"""Impossible dates must never crash and never fabricate a plausible span.

Two contracts are pinned here:

* the public edge NEVER raises -- a non-existent Nth weekday of a month
  ("the 5th Monday of February", when that February has only four Mondays)
  yields ``None``, not an ``IndexError`` (the HARD never-raise contract);
* an impossible calendar day is vetoed to ``None`` rather than silently
  fabricating a broader plausible-wrong span (residue-veto design,
  docs/design/errors-by-construction.md / #244).  "day 32 of February"
  must not fall back to the whole month; "the 366th day of the year 2017"
  must not fall back to the whole year.

Every VALID neighbour is pinned alongside so the veto cannot over-fire.
"""
import pytest

from ._corpus import ANCHOR, parse, nomatch, span
from chronologia.astrodate import AstroDate


# -- (1) never crash on a non-existent Nth weekday of a month -------------
# February 2017 has exactly four Mondays (6, 13, 20, 27): a 5th or 6th
# Monday does not exist.  The API must return None, never raise.
@pytest.mark.parametrize("text", [
    "the 5th Monday of February",
    "the 6th Monday of February 2017",
    "the 5th Monday of February 2017",
])
def test_nonexistent_nth_weekday_returns_none_not_raises(text):
    # must not raise -- the call itself is the assertion
    assert parse(text, ANCHOR) is None


# the Nth weekday that DOES exist still resolves (regression pins).
def test_fourth_monday_of_february_still_resolves():
    assert span("the 4th Monday of February").start == AstroDate(2017, 2, 27)


def test_last_monday_of_february_still_resolves():
    assert span("the last Monday of February").start == AstroDate(2017, 2, 27)


# -- (2) impossible calendar day -> None, never a fabricated span ---------
@pytest.mark.parametrize("text", [
    "the 29th of February this year",   # 2017 is not a leap year
    "the 29th of February 2017",
    "the 30th of February",
    "the 30th of February 2020",
    "the 31st of April",
    "the 32nd of February 2017",
    "day 32 of February 2017",
    "the 366th day of the year 2017",   # 2017 has 365 days
])
def test_impossible_day_vetoed_to_none(text):
    assert nomatch(text) is None


# -- valid neighbours the veto must NOT swallow (regression pins) ---------
def test_leap_day_2020_resolves():
    assert span("February 29 2020").start == AstroDate(2020, 2, 29)


def test_last_day_of_leap_year_resolves():
    # 2020 is a leap year: its 366th day is Dec 31.
    assert span("the 366th day of the year 2020").start == AstroDate(2020, 12, 31)


def test_365th_day_of_non_leap_year_resolves():
    assert span("the 365th day of the year 2017").start == AstroDate(2017, 12, 31)


def test_100th_day_of_year_resolves():
    assert span("the 100th day of the year").start == AstroDate(2017, 4, 10)


def test_thirty_first_of_march_resolves():
    assert span("the 31st of March").start == AstroDate(2018, 3, 31)


def test_twenty_eighth_of_february_2017_resolves():
    assert span("the 28th of February 2017").start == AstroDate(2017, 2, 28)
