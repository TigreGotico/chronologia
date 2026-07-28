# -*- coding: utf-8 -*-
"""Within-month day ranges (sl): ``od D1. do D2. <month gen> <year>``.

An inclusive day range inside one month resolves to
``[Y-M-D1 00:00, Y-M-D2+1 00:00)`` -- the end day is included, so ``.end`` is
the day after D2.  Gold is calendar arithmetic computed here.  Anchor:
Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

_PAIRS = [(1, 3), (5, 12), (10, 20), (20, 28)]
_YEARS = [2015, 2020]

_CASES = [
    (f"od {d1}. do {d2}. {GEN[m]} {y}", y, m, d1, d2)
    for y in _YEARS for m in range(1, 13) for (d1, d2) in _PAIRS
]


@pytest.mark.parametrize("text,y,m,d1,d2", _CASES)
def test_within_month_range(text, y, m, d1, d2):
    s, e = start_end(text)
    assert s == ad(datetime(y, m, d1))
    assert e == ad(datetime(y, m, d2) + timedelta(days=1))
