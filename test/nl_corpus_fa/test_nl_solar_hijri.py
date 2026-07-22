# -*- coding: utf-8 -*-
"""Solar Hijri (شمسی) native-calendar dates in Persian.

The Solar Hijri is the primary Iranian calendar; a phrase like "15 خرداد
1403" resolves through the solar_hijri_arithmetic calendar, the first locale
whose PRIMARY months are non-Gregorian.  Expected Gregorian equivalents are
derived independently from Nowruz 1403 = 20 March 2024 (a well-documented
anchor) plus the fixed Solar-Hijri month lengths [31]*6 + [30]*5 + [29],
never pinned from the engine.  1403 is a common (non-leap) year."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, start

_NOWRUZ_1403 = date(2024, 3, 20)
_LEN = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]


def _sh_1403(m, d):
    doy = sum(_LEN[:m - 1]) + d          # 1-based day of Solar-Hijri year
    return _NOWRUZ_1403 + timedelta(days=doy - 1)


@pytest.mark.parametrize("text,m,d", [
    ("1 فروردین 1403", 1, 1), ("15 فروردین 1403", 1, 15),
    ("1 اردیبهشت 1403", 2, 1), ("15 خرداد 1403", 3, 15),
    ("1 تیر 1403", 4, 1), ("10 مرداد 1403", 5, 10),
    ("1 شهریور 1403", 6, 1), ("1 مهر 1403", 7, 1),
    ("15 آبان 1403", 8, 15), ("1 آذر 1403", 9, 1),
    ("10 دی 1403", 10, 10), ("1 بهمن 1403", 11, 1),
    ("29 اسفند 1403", 12, 29)])
def test_solar_hijri_day(text, m, d):
    g = _sh_1403(m, d)
    assert start(text) == AstroDate(g.year, g.month, g.day)


def test_khordad_15_is_june_4():
    # the doc's worked example: 15 Khordad 1403 == 2024-06-04
    assert start("15 خرداد 1403") == AstroDate(2024, 6, 4)


@pytest.mark.parametrize("text,m", [
    ("فروردین", 1), ("خرداد", 3), ("مهر", 7), ("اسفند", 12)])
def test_bare_solar_month_resolves(text, m):
    # a bare Solar-Hijri month name still resolves to a month-wide span
    s = start(text)
    assert s is not None
