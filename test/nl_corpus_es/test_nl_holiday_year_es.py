# -*- coding: utf-8 -*-
"""Spanish holidays pinned to an explicit year: "Navidad 2021", "Reyes 2020",
"Miércoles de Ceniza 2020".

Fixed-date feasts land on their civil date in the named year.  Movable feasts
are pinned by their offset from Western-computus Easter, computed here by an
independent Anonymous-Gregorian implementation (:func:`_easter`) that never
touches the parser.  Every holiday is a single civil day.

The BARE-YEAR form ("Navidad 2021") is what the engine resolves; the "de <year>"
form ("Navidad de 2021") is on the campaign BUG list and is not asserted here.
Spanish holidays covered: Reyes (6 Jan), Asunción (15 Aug), Todos los Santos
(1 Nov), plus Navidad/Nochebuena/Nochevieja/Año Nuevo and the Easter cycle.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start, span


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
_YEARS = [2018, 2019, 2020, 2021, 2022]


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
def test_holiday_with_year(text, g):
    s = span(text)
    assert s.start == AstroDate(g.year, g.month, g.day), f"{text!r} -> {s.start}"
    assert s.width == timedelta(days=1)
