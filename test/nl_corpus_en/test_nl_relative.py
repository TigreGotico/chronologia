"""Wave 1 -- relative phrases: "in N units", "N units ago",
next/last/this weekday, named days, and the harder idiomatic compounds.

Expected values come from independent Python date arithmetic against the
Tuesday 2017-06-27 13:04 anchor -- ``relative_offset`` shifts the whole
anchor datetime and keeps its time-of-day; ``named_day`` / ``weekday_ref``
land on midnight of the resolved day.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start, nomatch


# -- "N units ago" / "in N units", digit and spelled ----------------------

_NW = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
       7: "seven", 8: "eight", 9: "nine", 10: "ten", 12: "twelve",
       20: "twenty", 30: "thirty"}


def _day_cases():
    out = []
    for n in (1, 2, 3, 5, 10, 20, 30):
        out.append((f"{n} days ago", ANCHOR - timedelta(days=n)))
        out.append((f"in {n} days", ANCHOR + timedelta(days=n)))
        out.append((f"{_NW[n]} days ago", ANCHOR - timedelta(days=n)))
        out.append((f"in {_NW[n]} days", ANCHOR + timedelta(days=n)))
    return out


def _week_cases():
    out = []
    for n in (1, 2, 3, 4, 6):
        out.append((f"{n} weeks ago", ANCHOR - timedelta(weeks=n)))
        out.append((f"in {n} weeks", ANCHOR + timedelta(weeks=n)))
        out.append((f"in {_NW[n]} weeks", ANCHOR + timedelta(weeks=n)))
    return out


def _month_cases():
    out = []
    for n in (1, 2, 3, 6, 8, 12):
        out.append((f"{n} months ago", ANCHOR - relativedelta(months=n)))
        out.append((f"in {n} months", ANCHOR + relativedelta(months=n)))
    return out


def _year_cases():
    out = []
    for n in (1, 2, 3, 5, 10, 20):
        out.append((f"{n} years ago", ANCHOR - relativedelta(years=n)))
        out.append((f"in {n} years", ANCHOR + relativedelta(years=n)))
    return out


@pytest.mark.parametrize("text,expected",
                         _day_cases() + _week_cases()
                         + _month_cases() + _year_cases())
def test_relative_offset(text, expected):
    assert start(text) == ad(expected)


# -- named days (day-wide, midnight) --------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("today", ANCHOR.replace(hour=0, minute=0)),
    ("tomorrow", (ANCHOR + timedelta(days=1)).replace(hour=0, minute=0)),
    ("yesterday", (ANCHOR - timedelta(days=1)).replace(hour=0, minute=0)),
    ("overmorrow", (ANCHOR + timedelta(days=2)).replace(hour=0, minute=0)),
    ("ereyesterday", (ANCHOR - timedelta(days=2)).replace(hour=0, minute=0)),
])
def test_named_day(text, expected):
    assert start(text) == ad(expected)


# -- weekday_ref: next/last/this <weekday> --------------------------------
# hand-derived against the Tuesday anchor (weekday index 1)

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,expected", [
    ("next monday", _MID + timedelta(days=6)),      # 2017-07-03
    ("next tuesday", _MID + timedelta(days=7)),      # 2017-07-04
    ("next wednesday", _MID + timedelta(days=1)),    # 2017-06-28
    ("next thursday", _MID + timedelta(days=2)),     # 2017-06-29
    ("next friday", _MID + timedelta(days=3)),       # 2017-06-30
    ("next saturday", _MID + timedelta(days=4)),     # 2017-07-01
    ("next sunday", _MID + timedelta(days=5)),       # 2017-07-02
    ("last monday", _MID - timedelta(days=1)),       # 2017-06-26
    ("last tuesday", _MID - timedelta(days=7)),      # 2017-06-20
    ("last wednesday", _MID - timedelta(days=6)),    # 2017-06-21
    ("last thursday", _MID - timedelta(days=5)),     # 2017-06-22
    ("last friday", _MID - timedelta(days=4)),       # 2017-06-23
    ("last saturday", _MID - timedelta(days=3)),     # 2017-06-24
    ("last sunday", _MID - timedelta(days=2)),       # 2017-06-25
    ("this monday", _MID - timedelta(days=1)),       # week start (Mon)
    ("this tuesday", _MID),                          # anchor day
    ("this wednesday", _MID + timedelta(days=1)),
    ("this thursday", _MID + timedelta(days=2)),
    ("this friday", _MID + timedelta(days=3)),
    ("this saturday", _MID + timedelta(days=4)),
    ("this sunday", _MID + timedelta(days=5)),
])
def test_weekday_ref(text, expected):
    assert start(text) == ad(expected)


# -- day-wide vs offset width (referential span, not a point) -------------

def test_named_day_is_day_wide():
    from ._corpus import span
    assert span("tomorrow").width == timedelta(days=1)


def test_days_offset_is_day_wide():
    from ._corpus import span
    assert span("in 3 days").width == timedelta(days=1)


def test_weeks_offset_is_week_wide():
    from ._corpus import span
    assert span("in 2 weeks").width == timedelta(weeks=1)


# -- idiomatic compounds -------------------------------------------------

@pytest.mark.parametrize("text,days", [
    ("the day after tomorrow", 2), ("day after tomorrow", 2),
    ("the day before yesterday", -2),
])
def test_day_after_tomorrow(text, days):
    assert start(text) == ad((ANCHOR + timedelta(days=days)).replace(
        hour=0, minute=0))


@pytest.mark.parametrize("text,days", [
    ("a week from tuesday", 14), ("a week from monday", 6 + 7),
    ("two weeks from monday", 6 + 14), ("a week from friday", 3 + 7),
])
def test_a_week_from_weekday(text, days):
    assert start(text) == ad(_MID + timedelta(days=days))


@pytest.mark.parametrize("text,delta", [
    ("a fortnight ago", timedelta(weeks=-2)),
    ("in a fortnight", timedelta(weeks=2)),
    ("two fortnights ago", timedelta(weeks=-4)),
])
def test_a_fortnight(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("in a couple of weeks", timedelta(weeks=2)),
    ("a couple of weeks ago", timedelta(weeks=-2)),
    ("in a couple of days", timedelta(days=2)),
])
def test_couple_of(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("in half an hour", timedelta(minutes=30)),
    ("in an hour", timedelta(hours=1)),
    ("half an hour ago", timedelta(minutes=-30)),
    ("in 15 minutes", timedelta(minutes=15)),
    ("in two hours", timedelta(hours=2)),
])
def test_subday_offset(text, delta):
    assert start(text) == ad(ANCHOR + delta)


# adversarial: an offset phrase with no direction marker is not an offset.
def test_offset_needs_marker():
    from ._corpus import parse
    assert parse("half an hour of cleaning") is None
    assert parse("a couple of weeks") is None       # no ago/in
    assert parse("fortnight") is None
