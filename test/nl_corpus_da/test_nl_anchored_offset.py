"""Anchored arithmetic (da): a signed unit offset or a strict weekday roll
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
    ("2 uger efter påske", EASTER + timedelta(days=14)),
    ("3 dage efter juledag", XMAS + timedelta(days=3)),
    ("3 dage før påske", EASTER - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)

@pytest.mark.parametrize("text,expected", [
    ("mandag efter juledag", date(2018, 1, 1)),
    ("fredag før påske", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)

def test_week_offset_is_week_wide():
    assert span("2 uger efter påske").width == timedelta(days=7)

def test_bare_after_holiday_unchanged():
    assert start("efter påske") == _ad(EASTER)

@pytest.mark.parametrize("text", ['efter mødet', 'dagen efter mødet'])
def test_no_reference_no_offset(text):
    nomatch(text)
