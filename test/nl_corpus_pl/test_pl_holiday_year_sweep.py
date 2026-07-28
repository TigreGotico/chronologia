# -*- coding: utf-8 -*-
"""Polish holiday + explicit year, swept across years 2020-2025.

Fixed feasts carry a constant (month, day).  Movable Easter-cycle feasts are
derived from an INDEPENDENT Western computus (``dateutil.easter``): Wielkanoc =
Easter Sunday, Poniedziałek Wielkanocny = Easter + 1 day, Wielki Piątek =
Easter - 2 days.  Every expected date is computed here without touching the
parser.  A bare holiday+year resolves to a single calendar day.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import AstroDate, parse, span, start

_FIXED = {
    "nowy rok": (1, 1),
    "trzech króli": (1, 6),
    "wszystkich świętych": (11, 1),
    "boże narodzenie": (12, 25),
    "wigilia": (12, 24),
    "walentynki": (2, 14),
    "halloween": (10, 31),
}
_YEARS = range(2020, 2026)

# already asserted in test_nl_holiday_ref.py
_EXISTING = {("nowy rok", 2020), ("wielkanoc", 2020)}


def _cases():
    out = []
    for y in _YEARS:
        golds = {h: date(y, m, d) for h, (m, d) in _FIXED.items()}
        e = easter(y)
        golds["wielkanoc"] = e
        golds["poniedziałek wielkanocny"] = e + timedelta(days=1)
        golds["wielki piątek"] = e - timedelta(days=2)
        for h, g in golds.items():
            if (h, y) in _EXISTING:
                continue
            out.append((f"{h} {y}", g))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gold", _CASES, ids=[c[0] for c in _CASES])
def test_holiday_year(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,gold", _CASES[::11], ids=[c[0] for c in _CASES[::11]])
def test_holiday_is_one_day(text, gold):
    assert span(text).width == timedelta(days=1)
