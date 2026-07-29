# -*- coding: utf-8 -*-
"""Second-pass sweep: every Portuguese holiday name (fixed feasts, civil
feasts, and the movable Easter cycle) x twenty years spread across two fresh
decades on each side of the anchor year (2017), none overlapping the
hand-picked samples already pinned in test_nl_national_holidays.py (which
covers 2017-2019) or test_nl_movable_feasts.py (2018 only).  The Easter
computus and every offset are re-derived here from first principles,
independent of the parser and independent of the existing corpus module.

Movable-feast offsets from Easter Sunday (day 0), hand-verified:
    Carnaval (Terça-feira de Carnaval) -- Easter - 47
    Sexta-feira Santa (Good Friday)    -- Easter - 2
    Páscoa (Easter Sunday)             -- Easter + 0
    Corpo de Deus (Corpus Christi)     -- Easter + 60

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


_YEARS = [1997, 1999, 2001, 2004, 2008, 2011, 2013, 2016,
          2027, 2029, 2031, 2033, 2036, 2039, 2041, 2044, 2046, 2049, 2051, 2054]

# fixed-date feasts: name -> (month, day)
_FIXED = {
    "ano novo": (1, 1),
    "assunção": (8, 15),
    "todos os santos": (11, 1),
    "natal": (12, 25),
}

# civil feasts bound by name (see test_nl_national_holidays.py)
_CIVIL = {
    "dia da liberdade": (4, 25),
    "dia do trabalhador": (5, 1),
    "dia de portugal": (6, 10),
    "implantação da república": (10, 5),
    "restauração da independência": (12, 1),
    "imaculada conceição": (12, 8),
}

# movable feasts: name -> offset (days) from Easter Sunday
_MOVABLE = {
    "carnaval": -47,
    "sexta-feira santa": -2,
    "páscoa": 0,
    "corpo de deus": 60,
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
