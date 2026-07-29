# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Spanish holidays pinned to explicit years spanning
several DECADES, not just the 2018-2022 band already covered by
``test_nl_holiday_year_es.py``.

Same fixed-date feasts and Easter-relative movable feasts as that file
(duplicated here for standalone readability); the only new axis is the year
list, chosen to avoid any overlap with the existing 2018-2022 grid or the
2017 anchor-year bare forms in ``test_nl_national_holidays.py``.

Movable-feast gold uses the same independent Anonymous-Gregorian Easter
algorithm, spot-verified against real calendars for 2000 (Ash Wednesday
2000-03-08) and 2050 (Pentecost 2050-05-29) before this file was written.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start


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
    mo = (h + l - 7 * m + 114) // 31
    da = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, mo, da)


_FIXED = {
    "navidad": (12, 25),
    "nochebuena": (12, 24),
    "reyes": (1, 6),
    "día de reyes": (1, 6),
    "asunción": (8, 15),
    "todos los santos": (11, 1),
    "san valentín": (2, 14),
    "noche de brujas": (10, 31),
    "nochevieja": (12, 31),
    "año nuevo": (1, 1),
}
_MOVABLE = {
    "miércoles de ceniza": -46,
    "domingo de ramos": -7,
    "jueves santo": -3,
    "viernes santo": -2,
    "sábado santo": -1,
    "pascua": 0,
    "pentecostés": 49,
}
# decades away from the existing 2017-anchor / 2018-2022 grids
_YEARS = [
    1990, 1995, 1998, 2000, 2001, 2003, 2005, 2010, 2011, 2015,
    2016, 2025, 2028, 2030, 2033, 2035, 2040, 2044, 2045, 2050,
]


def _cases():
    out = []
    for name, (mo, da) in _FIXED.items():
        for y in _YEARS:
            out.append((f"{name} {y}", date(y, mo, da)))
    for name, off in _MOVABLE.items():
        for y in _YEARS:
            out.append((f"{name} {y}", _easter(y) + timedelta(days=off)))
    return out


@pytest.mark.parametrize("text,g", _cases())
def test_holiday_with_decade_year(text, g):
    s = span(text)
    assert s.start == AstroDate(g.year, g.month, g.day), f"{text!r} -> {s.start}"
    assert s.width == timedelta(days=1)


# -- fixed civil holidays covered separately in test_nl_national_holidays.py
# (día del trabajador/trabajo, inmaculada, fiesta nacional/hispanidad,
# constitución) get the same decade-year treatment here.
_CIVIL_FIXED = {
    "día del trabajador": (5, 1),
    "día del trabajo": (5, 1),
    "inmaculada concepción": (12, 8),
    "fiesta nacional": (10, 12),
    "día de la hispanidad": (10, 12),
    "día de la constitución": (12, 6),
}


def _civil_cases():
    out = []
    for name, (mo, da) in _CIVIL_FIXED.items():
        for y in _YEARS:
            out.append((f"{name} {y}", date(y, mo, da)))
    return out


@pytest.mark.parametrize("text,g", _civil_cases())
def test_civil_holiday_with_decade_year(text, g):
    assert start(text) == AstroDate(g.year, g.month, g.day), text
