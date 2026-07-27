# -*- coding: utf-8 -*-
"""Anchored arithmetic (fa): ``N <unit> بعد از/قبل از <holiday>`` (signed unit
offset) and ``<weekday> بعد از/قبل از <holiday>`` (strict weekday roll) on a
resolved reference.  Anchor 2017-06-27 (Tuesday); نوروز 2018 = Wednesday
2018-03-21."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import span, start, nomatch

NOWRUZ = date(2018, 3, 21)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 هفته بعد از نوروز", NOWRUZ + timedelta(days=21)),
    ("1 هفته بعد از نوروز", NOWRUZ + timedelta(days=7)),
    ("5 روز بعد از نوروز", NOWRUZ + timedelta(days=5)),
    ("3 روز قبل از نوروز", NOWRUZ - timedelta(days=3)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("جمعه بعد از نوروز", date(2018, 3, 23)),
    ("شنبه بعد از نوروز", date(2018, 3, 24)),
    ("یکشنبه قبل از نوروز", date(2018, 3, 18)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("3 هفته بعد از نوروز").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("جمعه بعد از نوروز").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["قبل از جلسه", "بعد از ناهار"])
def test_no_reference_no_offset(text):
    nomatch(text)
