"""Anchored arithmetic (feature 1), Spanish.

"2 semanas después de pascua", "el lunes después de navidad" -- a signed
unit offset or strict weekday roll on a resolved reference, tolerating the
article/"de" gap.  Anchor 2017-06-27 (martes); pascua 2018 = dom 2018-04-01,
navidad = lun 2017-12-25.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start, nomatch

PASCUA = date(2018, 4, 1)
NAVIDAD = date(2017, 12, 25)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 semanas después de pascua", PASCUA + timedelta(days=14)),
    ("una semana después de pascua", PASCUA + timedelta(days=7)),
    ("1 semana antes de pascua", PASCUA - timedelta(days=7)),
    ("2 semanas antes de navidad", NAVIDAD - timedelta(days=14)),
    ("3 días antes de navidad", NAVIDAD - timedelta(days=3)),
    ("10 días después de navidad", NAVIDAD + timedelta(days=10)),
    ("el día después de navidad", NAVIDAD + timedelta(days=1)),
    ("1 mes después de pascua", date(2018, 5, 1)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("el lunes después de navidad", date(2018, 1, 1)),
    ("el viernes después de navidad", date(2017, 12, 29)),
    ("el martes antes de navidad", date(2017, 12, 19)),
    ("el domingo después de pascua", date(2018, 4, 8)),
    ("el sábado antes de pascua", date(2018, 3, 31)),
    ("el viernes antes de pascua", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span("2 semanas después de pascua").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span("el lunes después de navidad").width == timedelta(days=1)


def test_bare_after_holiday_unchanged():
    assert start("después de pascua") == _ad(PASCUA)


@pytest.mark.parametrize("text", ["antes de la reunión", "el día después de la boda"])
def test_no_reference_no_offset(text):
    nomatch(text)
