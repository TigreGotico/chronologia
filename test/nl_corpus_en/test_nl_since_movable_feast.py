""""since easter" opens at the most recent Easter, on its own date that year.

A holiday computed per year (Easter, Pentecost, Carnival, Chinese New Year)
falls on another month and day each year.  So the start of a "since" span,
and the left end of a range that is pulled back a year, is that year's own
date of the holiday, not the next date moved back by a calendar year.

Easter comes from ``dateutil.easter`` (the Gregorian computus): 20 April 2025,
5 April 2026 and 28 March 2027.  Pentecost is Easter plus 49 days, and
Carnival Tuesday is Easter minus 47 days.  Chinese New Year is 29 January 2025
and 17 February 2026 (Hong Kong Observatory, Gregorian-Lunar Calendar
Conversion Table).

Winter holds 1 January.  chronologia reads the meteorological winter,
1 December to 1 March (``chronologia/edtf.py``).  So the most recent winter
start before 20 June 2026 or 1 March 2026 is 1 December 2025, not the winter
that holds 1 January 2025.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import ad, parse

JUN20 = datetime(2026, 6, 20, 12, 0)
MAR01 = datetime(2026, 3, 1, 12, 0)
SEP01 = datetime(2026, 9, 1, 12, 0)
LEAP_DAY = datetime(2028, 2, 29, 12, 0)
DEC26 = datetime(2026, 12, 26, 12, 0)
FEB01 = datetime(2026, 2, 1, 12, 0)


def _day(d):
    return datetime(d.year, d.month, d.day)


EASTER_2025 = _day(easter(2025))
EASTER_2026 = _day(easter(2026))
EASTER_2027 = _day(easter(2027))
PENTECOST_2026 = EASTER_2026 + timedelta(days=49)
CARNIVAL_2026 = EASTER_2026 - timedelta(days=47)
CNY_2025 = datetime(2025, 1, 29)
CNY_2026 = datetime(2026, 2, 17)


@pytest.mark.parametrize("text,anchor,expected", [
    ("since easter", JUN20, EASTER_2026),
    ("since easter", MAR01, EASTER_2025),
    ("since easter", LEAP_DAY, EASTER_2027),
    ("since pentecost", JUN20, PENTECOST_2026),
    ("since carnival", JUN20, CARNIVAL_2026),
    ("since chinese new year", JUN20, CNY_2026),
    ("since chinese new year", FEB01, CNY_2025),
    ("since winter", JUN20, datetime(2025, 12, 1)),
    ("since winter", MAR01, datetime(2025, 12, 1)),
])
def test_since_movable_feast_is_its_own_date(text, anchor, expected):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""


# 1 Ramadan in the Umm al-Qura calendar: 18 February 2026 (1447), 28 January
# 2028 (1449), 16 January 2029 (1450).  The holiday reader can give a
# Ramadan that has ended, so the search must stop when a reading does not move
# on.
@pytest.mark.parametrize("anchor,expected", [
    (JUN20, datetime(2026, 2, 18)),
    (datetime(2028, 6, 1, 12, 0), datetime(2028, 1, 28)),
    (datetime(2029, 6, 1, 12, 0), datetime(2029, 1, 16)),
])
def test_since_ramadan_is_its_own_date(anchor, expected):
    r = parse("since ramadan", anchor)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""


@pytest.mark.parametrize("text,anchor,begin,end", [
    ("from easter to today", JUN20, EASTER_2026, datetime(2026, 6, 21)),
    ("since easter until today", JUN20, EASTER_2026, datetime(2026, 6, 21)),
    ("from easter to the 3rd of the month", SEP01, EASTER_2026,
     datetime(2026, 9, 4)),
    ("from easter to september 3", SEP01, EASTER_2026, datetime(2026, 9, 4)),
    ("from chinese new year to today", JUN20, CNY_2026,
     datetime(2026, 6, 21)),
    ("since winter until today", JUN20, datetime(2025, 12, 1),
     datetime(2026, 6, 21)),
    # Monday 2026-12-28: the most recent Friday is 25 December.
    ("from friday to today", datetime(2026, 12, 28, 12, 0),
     datetime(2026, 12, 25), datetime(2026, 12, 29)),
])
def test_range_from_movable_feast_is_its_own_date(text, anchor, begin, end):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# A definite left names one day counted from now, so the year pull leaves it.
# On Thursday 2026-12-31, tomorrow is 1 January 2027, two days from now is
# 2 January 2027 at 12:00, and next week starts on Monday 4 January 2027; each
# lies after the right end, so no range is read.
DEC31 = datetime(2026, 12, 31, 12, 0)


@pytest.mark.parametrize("text,begin,end", [
    ("from tomorrow to today", datetime(2027, 1, 1), datetime(2027, 1, 2)),
    ("from next week to december 31", datetime(2027, 1, 4),
     datetime(2027, 1, 11)),
    ("from the following week to december 31", datetime(2027, 1, 4),
     datetime(2027, 1, 11)),
    ("from two days from now to december 31", datetime(2027, 1, 2, 12),
     datetime(2027, 1, 3, 12)),
])
def test_definite_left_is_not_pulled_back_a_year(text, begin, end):
    r = parse(text, DEC31)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder != ""


# A bare clock recurs daily, so it is rolled back by days, never by a year:
# the left end is the latest reading that starts before the right end.  On
# Thursday 31 December the year pull read 30 December 09:00.  A clock with a
# weekday keeps the yearly reading: the most recent Friday is 25 December.
DEC31_13 = datetime(2026, 12, 31, 13, 0)
JUN15_13 = datetime(2026, 6, 15, 13, 0)


@pytest.mark.parametrize("text,anchor,begin,end", [
    ("from 9am to today", DEC31_13, datetime(2026, 12, 31, 9),
     datetime(2027, 1, 1)),
    ("from 9am to today", JUN15_13, datetime(2026, 6, 15, 9),
     datetime(2026, 6, 16)),
    ("from 9am to now", DEC31_13, datetime(2026, 12, 31, 9), DEC31_13),
    ("from midnight to today", DEC31_13, datetime(2026, 12, 31),
     datetime(2027, 1, 1)),
    ("from 9am to yesterday", JUN15_13, datetime(2026, 6, 14, 9),
     datetime(2026, 6, 15)),
    ("from 9am on friday to today", DEC31_13, datetime(2026, 12, 25, 9),
     datetime(2027, 1, 1)),
])
def test_a_clock_is_rolled_back_by_days(text, anchor, begin, end):
    r = parse(text, anchor)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


@pytest.mark.parametrize("anchor,expected", [
    (JUN20, datetime(2025, 12, 25)),
    (MAR01, datetime(2025, 12, 25)),
    (DEC26, datetime(2026, 12, 25)),
])
def test_since_christmas_unchanged(anchor, expected):
    r = parse("since christmas", anchor)
    assert r is not None
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""
