# -*- coding: utf-8 -*-
"""Bare Solar-Hijri month + year -> whole-month span in Persian.

``خرداد 1403`` resolves to the half-open span [1 Khordad, 1 Tir).  Both
endpoints come from the independent ``_jalali`` oracle.  Only months 1..11 are
swept so the exclusive end stays inside the same (concordant) year; Esfand is
excluded because its end rolls into the next Nowruz.  Year 1404 is omitted for
the same reason as the full-date sweep.
"""
import pytest

from ._corpus import ad, start_end
from ._jalali import JMON, j2g

_YEARS = [1398, 1399, 1400, 1401, 1402, 1403, 1405]


@pytest.mark.parametrize("text,y,m", [
    (f"{JMON[m - 1]} {y}", y, m) for y in _YEARS for m in range(1, 12)
])
def test_solar_hijri_month_year_span(text, y, m):
    from datetime import datetime
    s = j2g(y, m, 1)
    e = j2g(y, m + 1, 1)
    got = start_end(text)
    assert got == (ad(datetime(s.year, s.month, s.day)),
                   ad(datetime(e.year, e.month, e.day)))
