# -*- coding: utf-8 -*-
"""Turkish calendar sweeps: day+month (no year), month+year, bare year.

Bare "gün ay" resolves to the next occurrence on or after the anchor; the
oracle picks the year by the same on-or-after rule, computed independently of
the parser.  Month+year and bare-year spans are pinned to their arithmetic
edges.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import span, start, start_end

A = datetime(2017, 6, 27, 13, 4)
_AD = A.date()

_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}


def _next_year(m, d):
    """Year of the next on-or-after occurrence of (m, d) from the anchor."""
    return 2017 if date(2017, m, d) >= _AD else 2018


# -- bare day+month (no year): next occurrence -------------------------------
def _dm_cases():
    out = []
    for m in range(1, 13):
        for d in (3, 15, 25):
            out.append((f"{d} {_MONTHS[m]}", m, d))
    return out


@pytest.mark.parametrize("text,m,d", _dm_cases())
def test_day_month_no_year(text, m, d):
    y = _next_year(m, d)
    assert start(text, A) == AstroDate(y, m, d)
    assert span(text, A).width == timedelta(days=1)


# -- month + year: whole calendar month --------------------------------------
def _my_cases():
    out = []
    for y in (1999, 2010, 2023, 2031):
        for m in range(1, 13):
            out.append((f"{_MONTHS[m]} {y}", y, m))
    return out


@pytest.mark.parametrize("text,y,m", _my_cases())
def test_month_year(text, y, m):
    s, e = start_end(text, A)
    assert s == AstroDate(y, m, 1)
    nm_y, nm_m = (y + 1, 1) if m == 12 else (y, m + 1)
    assert e == AstroDate(nm_y, nm_m, 1)


# -- bare year: whole calendar year ------------------------------------------
@pytest.mark.parametrize("y", [1901, 1950, 1984, 1999, 2008, 2020, 2033, 2040])
def test_bare_year(y):
    s, e = start_end(str(y), A)
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
