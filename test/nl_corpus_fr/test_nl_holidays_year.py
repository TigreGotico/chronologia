# -*- coding: utf-8 -*-
"""French holidays with an explicit year, over several years (fr).

Fixed feasts (Jour de l'An, Épiphanie, Assomption, Toussaint, Noël) are fixed
Gregorian dates.  The movable Easter cycle is computed here by an independent
anonymous-Gregorian computus and its offsets (Vendredi saint = -2, Lundi de
Pâques = +1, Ascension = +39, Pentecôte = +49, Lundi de Pentecôte = +50).
Neither the Easter table nor any offset is read back from the parser: the whole
point is to pin the engine's holiday resolver against arithmetic derived from
first principles.

Each holiday reference is one day wide.  Anchor Tuesday 2017-06-27 13:04, but
every case names its own year so the anchor only fixes the locale.

NOTE (locale-vocabulary gap, not asserted): the purely civil French holidays
"Fête du Travail" (1 mai), "Fête Nationale" (14 juillet) and "Armistice"
(11 novembre) do NOT bind by name in this locale -- the phrase is dropped and a
bare year span is returned.  Their fixed calendar dates ARE reachable through
the literal-date forms "le 1er mai 2019" / "le 14 juillet 2019" /
"le 11 novembre 2020", which are exercised below.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import span, start


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


_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

# fixed-date feasts: name -> (month, day)
_FIXED = {
    "jour de l'an": (1, 1),
    "épiphanie": (1, 6),
    "assomption": (8, 15),
    "toussaint": (11, 1),
    "noël": (12, 25),
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


def _movable_cases():
    out = []
    for name, off in _MOVABLE.items():
        for y in _YEARS:
            out.append((f"{name} {y}", _ad(_easter(y) + timedelta(days=off))))
    return out


@pytest.mark.parametrize("text,expected", _fixed_cases())
def test_fixed_holiday_year(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,expected", _movable_cases())
def test_movable_holiday_year(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)


# -- civil feasts reached as literal dates (see module note) -----------------

@pytest.mark.parametrize("text,expected", [
    ("le 1er mai 2019", AstroDate(2019, 5, 1)),
    ("le 14 juillet 2019", AstroDate(2019, 7, 14)),
    ("le 14 juillet 2020", AstroDate(2020, 7, 14)),
    ("le 11 novembre 2020", AstroDate(2020, 11, 11)),
    ("le 8 mai 2019", AstroDate(2019, 5, 8)),
])
def test_civil_holiday_as_literal_date(text, expected):
    assert start(text) == expected
    assert span(text).width == timedelta(days=1)
