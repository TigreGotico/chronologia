# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: cross-month day ranges (sl).

``od D1. MES1 do D2. MES2 LETO`` -- an inclusive day range that crosses a
month (and sometimes a year) boundary, e.g. ``od 20. decembra 2021 do
5. januarja 2022``.  Distinct from the already-covered within-month range
(``test_sl_within_month_range_sweep.py``, single month per case): here the
two endpoints name different months (and for the year-boundary cases,
different years).  Gold is inclusive-end calendar arithmetic computed here.
Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

# (d1, m1, d2, m2) -- month-crossing pairs within the same year.
_SAME_YEAR_PAIRS = [
    (20, 1, 5, 2), (15, 3, 3, 4), (28, 4, 10, 5), (25, 6, 8, 7),
    (30, 8, 12, 9), (22, 10, 4, 11),
]
_YEARS = [2018, 2022, 2024, 2029]

_CASES_SAME_YEAR = [
    (f"od {d1}. {GEN[m1]} do {d2}. {GEN[m2]} {y}", y, m1, d1, y, m2, d2)
    for y in _YEARS for (d1, m1, d2, m2) in _SAME_YEAR_PAIRS
]

# year-crossing ranges: end year is always the anchor year of the phrase.
_YEAR_CROSS = [
    (20, 12, 5, 1), (27, 12, 15, 1), (10, 12, 2, 1),
]
_START_YEARS = [2018, 2021, 2025]

_CASES_YEAR_CROSS = [
    (f"od {d1}. {GEN[12]} {y} do {d2}. {GEN[1]} {y + 1}", y, 12, d1, y + 1, 1, d2)
    for y in _START_YEARS for (d1, _m1, d2, _m2) in _YEAR_CROSS
]


@pytest.mark.parametrize("text,y1,m1,d1,y2,m2,d2", _CASES_SAME_YEAR + _CASES_YEAR_CROSS)
def test_cross_month_range(text, y1, m1, d1, y2, m2, d2):
    s0 = datetime(y1, m1, d1)
    e0 = datetime(y2, m2, d2) + timedelta(days=1)
    s, e = start_end(text)
    assert s == ad(s0)
    assert e == ad(e0)
