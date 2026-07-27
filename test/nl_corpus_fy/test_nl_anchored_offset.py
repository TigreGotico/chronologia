"""Anchored arithmetic (fy): a signed unit offset or a strict weekday roll
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
    ("2 wiken nei peaske", EASTER + timedelta(days=14)),
    ("3 dagen nei earste krystdei", XMAS + timedelta(days=3)),
    ("3 dagen foar peaske", EASTER - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)

@pytest.mark.parametrize("text,expected", [
    ("moandei nei earste krystdei", date(2018, 1, 1)),
    ("freed foar peaske", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)

# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 wiken nei peaske").width == timedelta(days=1)

def test_bare_after_holiday_unchanged():
    assert start("nei peaske") == _ad(EASTER)

@pytest.mark.parametrize("text", ['nei de gearkomste', 'de dei nei de gearkomste'])
def test_no_reference_no_offset(text):
    nomatch(text)
