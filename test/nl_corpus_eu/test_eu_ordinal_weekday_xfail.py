# -*- coding: utf-8 -*-
"""Basque ordinal-weekday-in-month resolves to the exact day.

"2018ko martxoaren hirugarren astelehena" ("the third Monday of March 2018")
lands on 2018-03-19.  The Basque surface is postposed -- MONTH-genitive then
ORDINAL then WEEKDAY-absolutive, year (``-ko``) leading -- wired via the
``scoped_ordinal`` order "YEAR? MONTH ORD WEEKDAY" plus spelled-ordinal folding
(lehen(engo)/bigarren/hirugarren ...).  Each case pins the independently
computed day.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ad, start
from ._sweep import MONTH_GEN

ORD = {"lehen": 1, "bigarren": 2, "hirugarren": 3, "laugarren": 4}
WD = {"astelehena": 0, "asteartea": 1, "asteazkena": 2, "osteguna": 3,
      "ostirala": 4, "larunbata": 5, "igandea": 6}


def _nth_weekday(y, mo, wd, n):
    first = date(y, mo, 1)
    day = 1 + ((wd - first.weekday()) % 7) + (n - 1) * 7
    return datetime(y, mo, day)


CASES = [
    (2018, 3, "hirugarren", "astelehena"),
    (2018, 3, "lehen", "astelehena"),
    (2020, 11, "lehen", "astelehena"),
    (2021, 6, "bigarren", "igandea"),
    (2019, 5, "laugarren", "ostirala"),
    (2024, 1, "bigarren", "asteartea"),
]


@pytest.mark.parametrize("y,mo,ordw,wdw", CASES)
def test_ordinal_weekday(y, mo, ordw, wdw):
    text = f"{y}ko {MONTH_GEN[mo]} {ordw} {wdw}"
    gold = _nth_weekday(y, mo, WD[wdw], ORD[ordw])
    # sanity: the computed day really is that weekday in that month
    assert gold.weekday() == WD[wdw] and gold.month == mo
    assert start(text) == ad(gold)
