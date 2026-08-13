"""Anchored arithmetic (nl): a signed unit offset or a strict weekday roll
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
    ("2 weken na pasen", EASTER + timedelta(days=14)),
    ("3 dagen na eerste kerstdag", XMAS + timedelta(days=3)),
    ("3 dagen voor pasen", EASTER - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)

@pytest.mark.parametrize("text,expected", [
    ("maandag na eerste kerstdag", date(2018, 1, 1)),
    ("vrijdag voor pasen", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)

# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 weken na pasen").width == timedelta(days=1)

def test_bare_after_holiday_refused():
    # R146: a bare "after <holiday>" with no offset pre-amble used to answer
    # the holiday itself with the direction word stranded -- a defect. A
    # DateSpan cannot express an open-ended future, so it is refused outright.
    # See test_nl_r146_before_after_holiday.py (en) for the full writeup.
    nomatch("na pasen")

@pytest.mark.parametrize("text", ['na de vergadering', 'de dag na de vergadering'])
def test_no_reference_no_offset(text):
    nomatch(text)
