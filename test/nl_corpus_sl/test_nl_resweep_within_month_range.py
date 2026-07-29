# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: within-month day ranges (sl), FRESH years.

Same grammar as ``test_sl_within_month_range_sweep.py`` (``od D1. do D2.
<month gen> <year>``) but over years not previously exercised there (2015,
2020).  Gold is inclusive-end calendar arithmetic.  Anchor: Tuesday
2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

_PAIRS = [(2, 6), (7, 14), (11, 19), (23, 27)]
_YEARS = [2023, 2026]

_CASES = [
    (f"od {d1}. do {d2}. {GEN[m]} {y}", y, m, d1, d2)
    for y in _YEARS for m in range(1, 13) for (d1, d2) in _PAIRS
]


@pytest.mark.parametrize("text,y,m,d1,d2", _CASES)
def test_within_month_range_fresh(text, y, m, d1, d2):
    s, e = start_end(text)
    assert s == ad(datetime(y, m, d1))
    assert e == ad(datetime(y, m, d2) + timedelta(days=1))
