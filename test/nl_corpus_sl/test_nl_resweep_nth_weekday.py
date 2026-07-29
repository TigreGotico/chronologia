# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: nth-weekday-of-month (sl), FRESH years.

``tretji ponedeljek v marcu 2022`` = the 3rd Monday of March 2022; ``zadnji
petek v novembru 2025`` = the last Friday of November 2025.  The engine now
resolves the ordinal scope + locative month + year correctly for all seven
weekdays (verified live -- this grammar was previously broken and is still
covered, xfail, in ``test_sl_ordinal_weekday_of_month_broken.py`` for years
2018-2021; this file exercises the FRESH years 2022 and 2025 to avoid
duplicating those cases).  Gold is independent calendar arithmetic against
``datetime``, never the parser's own output.  Anchor: Tuesday 2017-06-27
13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {
    1: 'januarja', 2: 'februarja', 3: 'marca', 4: 'aprila', 5: 'maja',
    6: 'junija', 7: 'julija', 8: 'avgusta', 9: 'septembra', 10: 'oktobra',
    11: 'novembra', 12: 'decembra',
}
WD = {
    'ponedeljek': 0, 'torek': 1, 'sreda': 2, 'četrtek': 3, 'petek': 4,
    'sobota': 5, 'nedelja': 6,
}
ORD = {'prvi': 1, 'drugi': 2, 'tretji': 3, 'četrti': 4}
_YEARS = [2022, 2025]


def _nth_weekday(y, m, weekday, n):
    first = datetime(y, m, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(y, m, weekday):
    nxt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    last = nxt - timedelta(days=1)
    offset = (last.weekday() - weekday) % 7
    return last - timedelta(days=offset)


_NTH = [
    (f"{ordw} {wd} v {GEN[m]} {y}", y, m, wd, ordw)
    for y in _YEARS for m in range(1, 13) for wd in WD for ordw in ORD
]

_LAST = [
    (f"zadnji {wd} v {GEN[m]} {y}", y, m, wd)
    for y in _YEARS for m in range(1, 13) for wd in WD
]


@pytest.mark.parametrize("text,y,m,wd,ordw", _NTH)
def test_nth_weekday_of_month_fresh(text, y, m, wd, ordw):
    d0 = _nth_weekday(y, m, WD[wd], ORD[ordw])
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))


@pytest.mark.parametrize("text,y,m,wd", _LAST)
def test_last_weekday_of_month_fresh(text, y, m, wd):
    d0 = _last_weekday(y, m, WD[wd])
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))
