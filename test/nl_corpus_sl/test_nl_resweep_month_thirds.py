# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: month-thirds (sl), FRESH years.

Same grammar as ``test_sl_month_thirds_year_sweep.py`` (začetek/sredina/
konec + genitive month + year) but over years not previously exercised
there (2019, 2020).  Gold is 1/3 and 2/3 month-duration arithmetic against
``datetime``.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}
PARTS = ('začetek', 'sredina', 'konec')


def _thirds(y, m):
    f = datetime(y, m, 1)
    n = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    total = n - f
    b1 = f + total / 3
    b2 = f + total * 2 / 3
    return [(f, b1), (b1, b2), (b2, n)]


_YEARS = [2022, 2024]  # 2024 leap -> fresh 29-day February arithmetic
_CASES = [
    (f"{PARTS[i]} {GEN[m]} {y}", y, m, i)
    for y in _YEARS for m in range(1, 13) for i in range(3)
]


@pytest.mark.parametrize("text,y,m,i", _CASES)
def test_month_third_fresh(text, y, m, i):
    lo, hi = _thirds(y, m)[i]
    s, e = start_end(text)
    assert s == ad(lo)
    assert e == ad(hi)
