# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Slovenian public holidays, FRESH years.

Slovenia's civil calendar names ten fixed-date + two movable (Easter-linked)
public holidays.  A named holiday + year resolves to that one civil day:
``[Y-M-D 00:00, Y-M-D+1 00:00)``.  Movable-holiday gold (Velika noč /
Velikonočni ponedeljek) is computed with the Anonymous Gregorian (Meeus/
Jones/Butcher) Easter algorithm, independent of the parser.  Anchor: Tuesday
2017-06-27 13:04.

Verified live: five holidays resolve correctly (Novo leto, Božič, Velika
noč, Velikonočni ponedeljek, Dan spomina na mrtve).  The remaining seven --
Prešernov dan, Dan upora proti okupatorju, Praznik dela, Dan državnosti,
Marijino vnebovzetje, Dan reformacije, Dan samostojnosti -- fail to resolve
the holiday name at all: the engine matches only the trailing year token and
returns the *whole year* span with the holiday name stranded as residue
(e.g. ``dan državnosti 2022`` -> [2022-01-01, 2023-01-01) residue
``'dan državnosti'``).  Those are recorded here as strict xfails with the
CORRECT calendar gold, so a future fix flips them red.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

_YEARS_WORKING = [
    1901, 1917, 1933, 1949, 1960, 1972, 1984, 1990, 1999, 2005,
    2011, 2016, 2022, 2028, 2033, 2040, 2055, 2070, 2085, 2099,
]
_YEARS_XFAIL = [1925, 1944, 1963, 1981, 1997, 2013, 2022, 2035, 2058, 2091]


def _easter(y):
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a = y % 19
    b = y // 100
    c = y % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(y, month, day)


_FIXED_WORKING = [
    ('novo leto', 1, 1),
    ('božič', 12, 25),
    ('dan spomina na mrtve', 11, 1),
]

_CASES_FIXED = [
    (f"{name} {y}", y, m, d)
    for y in _YEARS_WORKING for (name, m, d) in _FIXED_WORKING
]


@pytest.mark.parametrize("text,y,m,d", _CASES_FIXED)
def test_holiday_fixed_working(text, y, m, d):
    d0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))


_CASES_MOVABLE = []
for _y in _YEARS_WORKING:
    _eas = _easter(_y)
    _CASES_MOVABLE.append((f"velika noč {_y}", _eas))
    _CASES_MOVABLE.append((f"velikonočni ponedeljek {_y}", _eas + timedelta(days=1)))


@pytest.mark.parametrize("text,d0", _CASES_MOVABLE)
def test_holiday_movable_working(text, d0):
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))


_FIXED_BROKEN = [
    ('prešernov dan', 2, 8),
    ('dan upora proti okupatorju', 4, 27),
    ('praznik dela', 5, 1),
    ('dan državnosti', 6, 25),
    ('marijino vnebovzetje', 8, 15),
    ('dan reformacije', 10, 31),
    ('dan samostojnosti', 12, 26),
]

_CASES_BROKEN = [
    (f"{name} {y}", y, m, d)
    for y in _YEARS_XFAIL for (name, m, d) in _FIXED_BROKEN
]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG: sl fixed-date holiday names (other than novo leto/božič/dan "
        "spomina na mrtve) are not matched -- only the trailing year is "
        "parsed and the holiday name is left as residue, so the engine "
        "returns the whole-year span instead of the single civil day."
    ),
)
@pytest.mark.parametrize("text,y,m,d", _CASES_BROKEN)
def test_holiday_fixed_broken(text, y, m, d):
    d0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))
