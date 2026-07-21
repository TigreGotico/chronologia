# -*- coding: utf-8 -*-
"""Scoped ordinals, seasons, decades and fuzzy month edges."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start, start_end, span, nomatch


def _week_of_month(n, year=2017, month=6):
    first = date(year, month, 1)
    d = first + timedelta(weeks=n) - timedelta(days=1)
    monday = d - timedelta(days=d.weekday())
    return AstroDate(monday.year, monday.month, monday.day)


@pytest.mark.parametrize("text,n", [("el primera semana de junio", 1), ("el segunda semana de junio", 2), ("el tercera semana de junio", 3)])
def test_week_of_month(text, n):
    assert start(text) == _week_of_month(n)
    assert span(text).width == timedelta(days=7)


def test_last_day_of_month():
    assert start("el último día de junio") \
        == AstroDate(2017, 6, 30)


# -- seasons (meteorological, 3 months, northern hemisphere) ---------------
@pytest.mark.parametrize("text,m", [
    ("primavera", 3), ("verano", 6),
    ("otoño", 9),
])
def test_season_anchor_year(text, m):
    s, e = start_end(text)
    assert s == AstroDate(2017, m, 1)


@pytest.mark.parametrize("text,y,m", [
    ("verano de 1969", 1969, 6),
    ("invierno de 1970", 1970, 12),
    ("primavera de 2000", 2000, 3),
])
def test_season_of_year(text, y, m):
    assert start(text) == AstroDate(y, m, 1)


# -- decades ("os anos noventa" / "els anys noranta") ----------------------
@pytest.mark.parametrize("text,base", [
    ("los años noventa", 1990),
    ("los años 90", 1990),
    ("años 80", 1980),
])
def test_decades(text, base):
    s, e = start_end(text)
    assert s == AstroDate(base, 1, 1)
    assert e == AstroDate(base + 10, 1, 1)


# -- fuzzy month edges (early third) ---------------------------------------
def test_early_month():
    s, e = start_end("principios de junio")
    assert s == AstroDate(2017, 6, 1)
    assert (e - s).days <= 11
