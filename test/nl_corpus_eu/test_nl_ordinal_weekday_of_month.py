# -*- coding: utf-8 -*-
"""Basque ordinal / last weekday-of-month, resolved to the exact day.

Basque postposes the whole construction: the month carries the genitive
(``martxoaren`` = of March), the ordinal is a spelled ``-garren`` word
(``lehen`` / ``bigarren`` / ``hirugarren`` ... , ``azken`` for the last), and
the weekday is absolutive (``astelehena`` = the Monday).  With a leading year
the surface is ``<YEAR>ko <MONTH-gen> <ORD> <WEEKDAY>``:

    "2018ko martxoaren hirugarren astelehena"  -> the 3rd Monday of March 2018

Every gold day is computed here by independent ``datetime`` arithmetic
(``_nth_weekday`` / ``_last_weekday``), never read back from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ad, start
from ._sweep import MONTH_GEN

#: spelled ordinal surfaces (idiomatic eu) -> value
ORD = {"lehen": 1, "lehenengo": 1, "bigarren": 2, "hirugarren": 3,
       "laugarren": 4, "bosgarren": 5}

#: absolutive weekday surfaces -> Monday=0 .. Sunday=6
WD = {"astelehena": 0, "asteartea": 1, "asteazkena": 2, "osteguna": 3,
      "ostirala": 4, "larunbata": 5, "igandea": 6}


def _nth_weekday(y, mo, wd, n):
    first = date(y, mo, 1)
    day = 1 + ((wd - first.weekday()) % 7) + (n - 1) * 7
    return datetime(y, mo, day)


def _last_weekday(y, mo, wd):
    # last day of the month, then step back to the wanted weekday
    nxt = date(y + (mo == 12), (mo % 12) + 1, 1)
    last = nxt - timedelta(days=1)
    back = (last.weekday() - wd) % 7
    d = last - timedelta(days=back)
    return datetime(d.year, d.month, d.day)


# ---- Nth weekday of a named month, year-led -------------------------------
NTH_CASES = [
    (2018, 3, "hirugarren", "astelehena"),   # 2018-03-19
    (2017, 1, "lehen", "astelehena"),        # 2017-01-02
    (2020, 11, "lehen", "astelehena"),       # 2020-11-02
    (2021, 6, "bigarren", "igandea"),        # 2021-06-13
    (2019, 5, "laugarren", "ostirala"),      # 2019-05-24
    (2024, 1, "bigarren", "asteartea"),      # 2024-01-09
    (2022, 9, "hirugarren", "osteguna"),     # 2022-09-15
    (2023, 12, "bosgarren", "larunbata"),    # 2023-12-30
    (2025, 2, "lehenengo", "asteazkena"),    # 2025-02-05
    (2016, 7, "laugarren", "igandea"),       # 2016-07-24
]


@pytest.mark.parametrize("y,mo,ordw,wdw", NTH_CASES)
def test_nth_weekday_of_month_year_led(y, mo, ordw, wdw):
    text = f"{y}ko {MONTH_GEN[mo]} {ordw} {wdw}"
    gold = _nth_weekday(y, mo, WD[wdw], ORD[ordw])
    assert gold.weekday() == WD[wdw] and gold.month == mo
    assert start(text) == ad(gold)


# ---- Nth weekday of a named month, no year (anchor year 2017) -------------
ANCHOR_Y = 2017
NTH_NOYEAR_CASES = [
    (1, "lehen", "astelehena"),       # 2017-01-02
    (3, "bigarren", "ostirala"),      # 2017-03-10
    (6, "hirugarren", "asteartea"),   # 2017-06-20
    (10, "laugarren", "igandea"),     # 2017-10-22
]


@pytest.mark.parametrize("mo,ordw,wdw", NTH_NOYEAR_CASES)
def test_nth_weekday_of_month_no_year(mo, ordw, wdw):
    text = f"{MONTH_GEN[mo]} {ordw} {wdw}"
    gold = _nth_weekday(ANCHOR_Y, mo, WD[wdw], ORD[ordw])
    assert gold.weekday() == WD[wdw] and gold.month == mo
    assert start(text) == ad(gold)


# ---- Last (azken) weekday of a named month --------------------------------
LAST_CASES = [
    (2017, 3, "ostirala"),    # 2017-03-31 (last Friday of March 2017)
    (2018, 5, "asteartea"),   # 2018-05-29
    (2020, 2, "larunbata"),   # 2020-02-29 (leap)
    (2021, 12, "osteguna"),   # 2021-12-30
    (2024, 8, "igandea"),     # 2024-08-25
    (2019, 11, "astelehena"), # 2019-11-25
]


@pytest.mark.parametrize("y,mo,wdw", LAST_CASES)
def test_last_weekday_of_month_year_led(y, mo, wdw):
    text = f"{y}ko {MONTH_GEN[mo]} azken {wdw}"
    gold = _last_weekday(y, mo, WD[wdw])
    assert gold.weekday() == WD[wdw] and gold.month == mo
    assert start(text) == ad(gold)


@pytest.mark.parametrize("mo,wdw", [(3, "ostirala"), (7, "astelehena"),
                                    (12, "igandea")])
def test_last_weekday_of_month_no_year(mo, wdw):
    text = f"{MONTH_GEN[mo]} azken {wdw}"
    gold = _last_weekday(ANCHOR_Y, mo, WD[wdw])
    assert gold.weekday() == WD[wdw] and gold.month == mo
    assert start(text) == ad(gold)
