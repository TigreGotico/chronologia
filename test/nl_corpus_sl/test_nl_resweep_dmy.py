# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: fully-specified day-month-year (sl), FRESH years.

Same grammar as ``test_sl_dmy_sweep.py`` (``15. marca 2020``, one civil day
wide) but over years not previously exercised there (1901, 1968, 2004, 2020,
2077).  Gold is pure calendar arithmetic.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

_DAYS = [2, 9, 17, 26]
_YEARS = [1923, 1977, 2011, 2035, 2090]

_CASES = [
    (f"{d}. {GEN[m]} {y}", y, m, d)
    for y in _YEARS for m in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,m,d", _CASES)
def test_dmy_genitive_fresh(text, y, m, d):
    s0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(s0)
    assert e == ad(s0 + timedelta(days=1))
