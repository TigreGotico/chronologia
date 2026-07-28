# -*- coding: utf-8 -*-
"""Italian holidays with an explicit year -- fixed and movable, several years.

Fixed dates are constants. Movable (Pasqua / Pasquetta) come from an in-file
Western computus (the anonymous Gregorian algorithm), computed independently of
the parser. Every holiday span is one day wide.

Only the holiday names this locale actually models as ``holiday_ref`` are
asserted here (Natale, Capodanno, Befana/Epifania, Ferragosto, Ognissanti,
Pasqua, Pasquetta). The purely civil Italian festivities -- Liberazione
(25 Apr), Festa del Lavoro (1 Mag), Festa della Repubblica (2 Giu),
Immacolata (8 Dic) -- do not currently bind as named holidays and are left to
the campaign BUG report rather than pinned here.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, AstroDate


def _easter(year):
    """Anonymous Gregorian computus -> date. Independent oracle."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


_YEARS = [2018, 2019, 2020, 2021]

_FIXED = {
    "natale": (12, 25),
    "capodanno": (1, 1),
    "befana": (1, 6),
    "ferragosto": (8, 15),
    "ognissanti": (11, 1),
}

_FIXED_CASES = [
    (f"{name} {y}", AstroDate(y, mo, d))
    for name, (mo, d) in _FIXED.items()
    for y in _YEARS
]


@pytest.mark.parametrize("text,gold", _FIXED_CASES)
def test_fixed_holiday_year(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(days=1)


_MOVABLE_CASES = []
for _y in _YEARS:
    _pasqua = _easter(_y)
    _MOVABLE_CASES.append((f"pasqua {_y}",
                           AstroDate(_pasqua.year, _pasqua.month, _pasqua.day)))
    _pq = _pasqua + timedelta(days=1)
    _MOVABLE_CASES.append((f"pasquetta {_y}",
                           AstroDate(_pq.year, _pq.month, _pq.day)))


@pytest.mark.parametrize("text,gold", _MOVABLE_CASES)
def test_movable_holiday_year(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(days=1)


def test_pasquetta_is_the_day_after_pasqua():
    for y in _YEARS:
        assert (span(f"pasquetta {y}").start - span(f"pasqua {y}").start
                == timedelta(days=1))
