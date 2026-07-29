# -*- coding: utf-8 -*-
"""Second-pass sweep: every French holiday name (fixed feasts, civil feasts,
and the movable Easter cycle) x twenty years spread across two fresh decades
on each side of the ones already pinned in test_nl_holidays_year.py
(2018-2025). The Easter computus and every offset are re-derived here from
first principles, independent of the parser and independent of the existing
corpus module.

Anchor Tuesday 2017-06-27 13:04, but every case names its own year so the
anchor only fixes the locale.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start, span


def _easter(y):
    a = y % 19
    b, c = y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, month, day)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


_YEARS = [1998, 2000, 2003, 2006, 2010, 2012, 2014, 2016,
          2026, 2028, 2030, 2032, 2035, 2038, 2040, 2043, 2045, 2048, 2050, 2053]

# fixed-date feasts: name -> (month, day)
_FIXED = {
    "jour de l'an": (1, 1),
    "assomption": (8, 15),
    "toussaint": (11, 1),
    "noël": (12, 25),
}

# civil feasts bound by name (see test_nl_national_holidays.py)
_CIVIL = {
    "fête du travail": (5, 1),
    "fête nationale": (7, 14),
    "armistice": (11, 11),
    "fête de la victoire": (5, 8),
}

# movable feasts: name -> offset (days) from Easter Sunday
_MOVABLE = {
    "pâques": 0,
    "vendredi saint": -2,
    "lundi de pâques": 1,
    "ascension": 39,
    "pentecôte": 49,
    "lundi de pentecôte": 50,
}


def _fixed_cases():
    return [(f"{name} {y}", _ad(date(y, mo, dd)))
            for name, (mo, dd) in _FIXED.items() for y in _YEARS]


def _civil_cases():
    return [(f"{name} {y}", _ad(date(y, mo, dd)))
            for name, (mo, dd) in _CIVIL.items() for y in _YEARS]


def _movable_cases():
    out = []
    for name, off in _MOVABLE.items():
        for y in _YEARS:
            out.append((f"{name} {y}", _ad(_easter(y) + timedelta(days=off))))
    return out


@pytest.mark.parametrize("text,expected", _fixed_cases())
def test_fixed_holiday_decades(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,expected", _civil_cases())
def test_civil_holiday_decades(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,expected", _movable_cases())
def test_movable_holiday_decades(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)
