"""Impossible calendar dates must return None, never a fabricated span.

Russian writes ordinals with a hyphenated suffix ("5-е" = пятое, "2-го" =
второго).  That surface must fold to its number so a day-of-month or an
Nth-weekday-of-month construction can bind -- otherwise the stray suffix
letter strands the ordinal and the reading silently widens to the whole
month (a fabrication).  Two never-fabricate contracts are pinned here:

* an Nth weekday of a month that has no such occurrence -- "5-е воскресенье
  февраля" (February 2017 has only four Sundays) -- is vetoed to None via the
  shared bounds-checked ``_nth_weekday_of_month`` (the same veto the spelled
  form "пятое воскресенье февраля" already gets);
* a bare out-of-range day glued to a month ("32 апреля") must not fall back
  to the whole month with the day dropped.

Every VALID neighbour -- including the hyphen-ordinal day-of-month and the
existing spelled-ordinal Nth-weekday -- is pinned so the veto cannot over-fire.
"""
import pytest

from ._corpus import ANCHOR, nomatch, span
from chronologia.astrodate import AstroDate


# -- Nth weekday of a month that does not exist -> None -------------------
@pytest.mark.parametrize("text", [
    "5-е воскресенье февраля",        # Feb 2017 has only four Sundays
    "пятое воскресенье февраля",      # the spelled form already vetoes
])
def test_nonexistent_nth_weekday_returns_none(text):
    nomatch(text)


# -- impossible calendar day -> None -------------------------------------
@pytest.mark.parametrize("text", [
    "32 апреля",              # no day 32 in any month
    "31 апреля",              # April has 30 days
    "30 февраля",             # February never has 30 days
    "29 февраля 2017",        # 2017 is not a leap year
])
def test_impossible_day_vetoed_to_none(text):
    nomatch(text)


# -- valid neighbours the veto must NOT swallow (regression pins) ---------
def test_second_sunday_of_february_resolves():
    # February 12 2017 is the 2nd Sunday -- both surfaces must agree.
    assert span("2-е воскресенье февраля").start == AstroDate(2017, 2, 12)
    assert span("второе воскресенье февраля").start == AstroDate(2017, 2, 12)


def test_hyphen_ordinal_day_of_month_resolves():
    # "5-е февраля" is Feb 5 -- the hyphen suffix must not strand the day.
    assert span("5-е февраля").start == AstroDate(2018, 2, 5)
    assert span("2-го февраля").start == AstroDate(2018, 2, 2)


def test_twenty_eight_february_resolves():
    assert span("28 февраля").start == AstroDate(2018, 2, 28)


def test_leap_day_2020_resolves():
    assert span("29 февраля 2020").start == AstroDate(2020, 2, 29)
