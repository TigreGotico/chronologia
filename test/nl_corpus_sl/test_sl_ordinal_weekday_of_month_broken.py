# -*- coding: utf-8 -*-
"""BUG: ordinal-weekday-of-month is not resolved for sl (strict xfail).

``tretji ponedeljek v marcu 2020`` means "the 3rd Monday of March 2020"
(= 2020-03-16).  On the current engine only the weekday token is consumed --
it returns the next weekday after the anchor and strands ``tretji v marcu
2020`` as residue (verified: start 2017-07-03, residue 'tretji v marcu 2020').
The ordinal scope, the locative month and the year are all dropped.

These tests assert the CORRECT calendar answer, computed here by independent
arithmetic, and are marked ``xfail(strict=True)``: they must fail until the
scoped-ordinal-weekday grammar is wired for sl, at which point the strict mark
flips them red so the fix is not missed.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad

GEN = {3: 'marca', 4: 'aprila', 6: 'junija', 9: 'septembra', 11: 'novembra'}
WD = {'ponedeljek': 0, 'torek': 1, 'sreda': 2, 'četrtek': 3, 'petek': 4}
ORD = {'prvi': 1, 'drugi': 2, 'tretji': 3, 'četrti': 4}


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
    ('tretji ponedeljek v marcu 2020', 2020, 3, 'ponedeljek', 'tretji'),
    ('prvi ponedeljek v marcu 2020', 2020, 3, 'ponedeljek', 'prvi'),
    ('drugi torek v aprilu 2021', 2021, 4, 'torek', 'drugi'),
    ('prvi petek v juniju 2019', 2019, 6, 'petek', 'prvi'),
    ('četrti četrtek v novembru 2018', 2018, 11, 'četrtek', 'četrti'),
]

_LAST = [
    ('zadnji petek v novembru 2019', 2019, 11, 'petek'),
    ('zadnji ponedeljek v marcu 2020', 2020, 3, 'ponedeljek'),
]


@pytest.mark.parametrize("text,y,m,wd,ordw", _NTH)  # fixed by PR #354
def test_nth_weekday_of_month(text, y, m, wd, ordw):
    d0 = _nth_weekday(y, m, WD[wd], ORD[ordw])
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))


@pytest.mark.xfail(strict=True, reason="sl scoped-ordinal-weekday not wired")
@pytest.mark.parametrize("text,y,m,wd", _LAST)
def test_last_weekday_of_month(text, y, m, wd):
    d0 = _last_weekday(y, m, WD[wd])
    s, e = start_end(text)
    assert s == ad(d0)
    assert e == ad(d0 + timedelta(days=1))
