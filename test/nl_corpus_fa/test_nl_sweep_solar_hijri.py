# -*- coding: utf-8 -*-
"""Broad Solar-Hijri (Jalali) full-date sweep in Persian.

Every expected Gregorian day is computed by the independent Borkowski oracle
in ``_jalali`` (never pinned from the engine).  Only concordant Jalali years
are swept: 1398-1403 and 1405.  Year 1404 is omitted on purpose -- there the
arithmetic and the engine's Solar-Hijri calendar disagree by a day, so its
gold is not certain.  Months 1..11 have fixed lengths; Esfand (month 12) is
swept only through day 29, present in both common and leap years.
"""
import pytest

from ._corpus import AstroDate, start
from ._jalali import JMON, j2g

_YEARS = [1398, 1399, 1400, 1401, 1402, 1403, 1405]
_DAYS = [1, 2, 3, 5, 8, 10, 12, 15, 18, 20, 22, 25, 28]


def _cases():
    out = []
    for y in _YEARS:
        for m in range(1, 12):          # months 1..11, fixed lengths
            for d in _DAYS:
                out.append((f"{d} {JMON[m - 1]} {y}", y, m, d))
        for d in [1, 5, 10, 15, 20, 25, 29]:   # Esfand, safe day range
            out.append((f"{d} {JMON[11]} {y}", y, 12, d))
    return out


@pytest.mark.parametrize("text,y,m,d", _cases())
def test_solar_hijri_full_date(text, y, m, d):
    g = j2g(y, m, d)
    assert start(text) == AstroDate(g.year, g.month, g.day)
