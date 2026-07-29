# -*- coding: utf-8 -*-
"""RESWEEP: Turkish "<month> <year>" whole-calendar-month spans, fresh years.

Disjoint year set from ``test_tr_calendar_sweep.py``'s
[1999, 2010, 2023, 2031] and its bare-year set
[1901, 1950, 1984, 1999, 2008, 2020, 2033, 2040].
Anchor: Tuesday 2017-06-27 13:04 (explicit years, so the anchor is inert).
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}

_YEARS = [1905, 1920, 1940, 1960, 1980, 1990, 2000, 2015, 2025, 2040]


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 13):
            out.append((f"{_MONTHS[m]} {y}", y, m))
    return out


@pytest.mark.parametrize("text,y,m", _cases())
def test_month_year_resweep(text, y, m):
    s, e = start_end(text, A)
    assert s == AstroDate(y, m, 1)
    nm_y, nm_m = (y + 1, 1) if m == 12 else (y, m + 1)
    assert e == AstroDate(nm_y, nm_m, 1)


# -- bare year: whole calendar year, fresh years -----------------------------
_BARE_YEARS = [1888, 1912, 1925, 1961, 1975, 1993, 2003, 2011, 2028, 2045]


@pytest.mark.parametrize("y", _BARE_YEARS)
def test_bare_year_resweep(y):
    s, e = start_end(str(y), A)
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
