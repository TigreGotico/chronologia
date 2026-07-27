"""Military zone-time as a clock, and a clock composed with a day-of-month.

Two number-vs-date collisions the parser used to lose:

1. A bare four-digit ``HHMM`` immediately qualified by a *military* time-zone
   word ("1500 Zulu", "1500 local", the glued "1500Z") is a 24-hour clock
   reading, not the year 1500.  The qualifier *licenses* the clock reading
   exactly as the "hours" marker already does ("at 1500 hours"); the leading
   digit no longer being zero is what previously mis-fired the year.  The
   wall clock is naive, mirroring the leading-zero military forms the library
   already resolved ("0300 Zulu", "0800Z"), which stay byte-identical.  A bare
   "1500" with *no* qualifier stays the year 1500.

2. A clock time that co-occurs with a day-of-month ("5pm on the 15th") is
   placed on *that* day, resolved by the existing day-of-month prefer-future
   month choice, instead of dropping the day and timing the anchor's own day.

Anchor: Tuesday 2017-06-27 13:04.  ``prefer_future`` rolls a wall time already
past today to tomorrow.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import span, start, parse


# ---------------------------------------------------------------------------
# 1. military zone-time reads as a clock (naive wall clock), not a year
# ---------------------------------------------------------------------------
# (text, y, mo, d, hh, mm) -- naive wall clock on the prefer-future day
_MIL_ZONE = [
    ("1500 Zulu",    2017, 6, 27, 15, 0),   # 15:00 > 13:04 -> today
    ("at 1500 Zulu", 2017, 6, 27, 15, 0),
    ("1500 local",   2017, 6, 27, 15, 0),
    ("at 1500 local", 2017, 6, 27, 15, 0),
    ("1500Z",        2017, 6, 27, 15, 0),   # glued Zulu suffix
    ("1200Z",        2017, 6, 28, 12, 0),   # 12:00 < 13:04 -> tomorrow
    ("2130 Zulu",    2017, 6, 27, 21, 30),
]


@pytest.mark.parametrize("text,y,mo,d,hh,mm", _MIL_ZONE)
def test_military_zone_time_is_a_clock(text, y, mo, d, hh, mm):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm)
    # naive wall clock -- mirrors the already-working leading-zero forms
    assert s.tzinfo is None


# already-working military forms: must stay byte-identical (naive wall clock,
# the zone/marker word behaviour unchanged).
_MIL_UNCHANGED = [
    ("at 1500 hours", 2017, 6, 27, 15, 0),
    ("0800Z",         2017, 6, 28, 8, 0),   # leading zero already a clock
    ("0300 Zulu",     2017, 6, 28, 3, 0),
]


@pytest.mark.parametrize("text,y,mo,d,hh,mm", _MIL_UNCHANGED)
def test_military_forms_unchanged(text, y, mo, d, hh, mm):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm)
    assert s.tzinfo is None


# a four-digit YEAR must NOT be hijacked by the clock reading: only a military
# zone/marker qualifier licenses the clock; a bare number stays a year.
_YEAR_PINS = [
    ("1500",          1500),
    ("in 1500",       1500),
    ("1500 AD",       1500),
    ("the year 1500", 1500),
]


@pytest.mark.parametrize("text,year", _YEAR_PINS)
def test_bare_four_digit_stays_year(text, year):
    s = span(text).start
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert (s.hour, s.minute) == (0, 0)


def test_year_range_unchanged():
    s = span("1500-2000")
    assert (s.start.year, s.end.year) == (1500, 2001)


# ---------------------------------------------------------------------------
# 2. a clock composes with a day-of-month ("5pm on the 15th")
# ---------------------------------------------------------------------------
# the day-of-month resolves by its own prefer-future month choice (June Nth has
# passed at the anchor, so it lands in July), then the clock sits on THAT day.
_CLOCK_ON_DAY = [
    ("5pm on the 15th",    AstroDate(2017, 7, 15, 17, 0)),
    ("at 3pm on the 10th", AstroDate(2017, 7, 10, 15, 0)),
    ("noon on the 1st",    AstroDate(2017, 7, 1, 12, 0)),
]


@pytest.mark.parametrize("text,want", _CLOCK_ON_DAY)
def test_clock_composes_with_day_of_month(text, want):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == \
        (want.year, want.month, want.day, want.hour, want.minute)


def test_plain_clock_still_times_anchor_day():
    s = start("5pm")
    assert (s.year, s.month, s.day, s.hour, s.minute) == (2017, 6, 27, 17, 0)
