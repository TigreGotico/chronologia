# -*- coding: utf-8 -*-
"""Anchored arithmetic (he): ``N <unit> אחרי/לפני <holiday>`` (signed unit
offset) and ``יום <weekday> אחרי/לפני <holiday>`` (strict weekday roll) on a
resolved reference.  Anchor 2017-06-27 (Tuesday); פסח 2018 = Saturday
2018-03-31.

Hebrew duals (יומיים "two days") are not folded to a number by the shared
numfold, so counts use an explicit digit or the singular ``שבוע`` (one).
Weekday rolls read the day-noun form, Monday ("יום שני") included -- the day
noun is what tells the ordinal apart from the cardinal "two"."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

PESACH = date(2018, 3, 31)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 שבועות אחרי פסח", PESACH + timedelta(days=21)),
    ("שבוע אחרי פסח", PESACH + timedelta(days=7)),
    ("5 ימים אחרי פסח", PESACH + timedelta(days=5)),
    ("3 ימים לפני פסח", PESACH - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("יום ראשון אחרי פסח", date(2018, 4, 1)),
    ("יום שישי אחרי פסח", date(2018, 4, 6)),
    ("יום חמישי אחרי פסח", date(2018, 4, 5)),
    ("יום שני אחרי פסח", date(2018, 4, 2)),
    ("יום ראשון לפני פסח", date(2018, 3, 25)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span("3 שבועות אחרי פסח").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span("יום ראשון אחרי פסח").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["לפני הפגישה", "אחרי הארוחה"])
def test_no_reference_no_offset(text):
    nomatch(text)
