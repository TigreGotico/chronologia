"""Anchored arithmetic (sv): a signed unit offset or a strict weekday roll
composed onto a resolved holiday reference. Anchor 2017-06-27 (Tue). Reference
dates from the independent computus/civil table: easter 2018 = Sun 2018-04-01,
christmas = Mon 2017-12-25."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

EASTER = date(2018, 4, 1)
XMAS = date(2017, 12, 25)

def _ad(dd):
    return AstroDate(dd.year, dd.month, dd.day)

@pytest.mark.parametrize("text,expected", [
    ("2 veckor efter påsk", EASTER + timedelta(days=14)),
    ("3 dagar efter juldagen", XMAS + timedelta(days=3)),
    ("3 dagar före påsk", EASTER - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)

@pytest.mark.parametrize("text,expected", [
    ("måndag efter juldagen", date(2018, 1, 1)),
    ("fredag före påsk", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)

def test_week_offset_is_week_wide():
    assert span("2 veckor efter påsk").width == timedelta(days=7)

def test_bare_after_holiday_unchanged():
    assert start("efter påsk") == _ad(EASTER)

@pytest.mark.parametrize("text", ['efter mötet', 'dagen efter mötet'])
def test_no_reference_no_offset(text):
    nomatch(text)
