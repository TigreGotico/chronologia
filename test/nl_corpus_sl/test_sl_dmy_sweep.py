# -*- coding: utf-8 -*-
"""Fully-specified day-month-year sweep (sl), idiomatic genitive month.

Slovenian writes a calendar date as ordinal-dot day + genitive month + year:
``15. marca 2020``.  A fully-specified date resolves to that civil day and is
exactly one day wide: ``[Y-M-D 00:00, Y-M-D+1 00:00)``.  Gold is pure calendar
arithmetic (``datetime`` + one-day delta) computed here, never read back from
the parser.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}

# days valid in every month (<= 28); years spanning past/future of the anchor.
_DAYS = [1, 3, 8, 15, 22, 28]
_YEARS = [1901, 1968, 2004, 2020, 2077]

_CASES = [
    (f"{d}. {GEN[m]} {y}", y, m, d)
    for y in _YEARS for m in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,m,d", _CASES)
def test_dmy_genitive(text, y, m, d):
    s0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(s0)
    assert e == ad(s0 + timedelta(days=1))


# leap-day and month-end boundaries: gold still one civil day.
_EDGE = [
    ("29. februarja 2020", 2020, 2, 29),   # leap
    ("28. februarja 2019", 2019, 2, 28),   # common-year Feb end
    ("31. decembra 2020", 2020, 12, 31),   # year rollover on .end
    ("30. aprila 1999", 1999, 4, 30),
    ("31. januarja 2000", 2000, 1, 31),
    ("1. januarja 1850", 1850, 1, 1),
    ("31. decembra 2099", 2099, 12, 31),
]


@pytest.mark.parametrize("text,y,m,d", _EDGE)
def test_dmy_edges(text, y, m, d):
    s0 = datetime(y, m, d)
    s, e = start_end(text)
    assert s == ad(s0)
    assert e == ad(s0 + timedelta(days=1))
