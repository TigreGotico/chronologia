# -*- coding: utf-8 -*-
"""Bare day-month (no year) sweep (sl): prefer-future resolution.

``5. junija`` with no year names the next occurrence of that calendar day.
The documented rule is strictly-future: take the (month, day) in the anchor's
year; if that civil date falls *before* the anchor's date, roll to the next
year.  Gold is computed here by that arithmetic, independent of the parser.
Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ANCHOR, start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

_DAYS = [1, 5, 10, 15, 20, 25, 28]


def _future_year(m, d):
    y = ANCHOR.year
    if date(y, m, d) < ANCHOR.date():
        y += 1
    return y


_CASES = [
    (f"{d}. {GEN[m]}", _future_year(m, d), m, d)
    for m in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,m,d", _CASES)
def test_bare_day_month_prefers_future(text, y, m, d):
    s0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(s0)
    assert e == ad(s0 + timedelta(days=1))
