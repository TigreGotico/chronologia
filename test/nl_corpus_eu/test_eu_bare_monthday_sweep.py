# -*- coding: utf-8 -*-
"""Oracle sweep: yearless Basque month-day rolls to its next occurrence.

Two idioms, same reckoning against the Tuesday 2017-06-27 anchor: the genitive
``MONTHgen DAY(an)`` ("martxoaren 8an") and the colloquial absolutive-plural
``MONTHak DAY`` ("martxoak 8").  A yearless date lands on the first occurrence
on or after the anchor date: year 2017 when (month, day) >= (6, 27), else 2018.
Gold is independent ``datetime`` arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start, start_end
from ._sweep import MONTH_AK, MONTH_GEN

ANCHOR_MD = (6, 27)
# days that exist in every month, so the sweep never hits an invalid date
DAYS = [1, 5, 11, 17, 23, 28]


def _rolled(mo, d):
    y = 2017 if (mo, d) >= ANCHOR_MD else 2018
    return datetime(y, mo, d)


def _gen(builder):
    return [(builder(mo, d), mo, d) for mo in range(1, 13) for d in DAYS]


GEN_CASES = _gen(lambda mo, d: f"{MONTH_GEN[mo]} {d}an")
AK_CASES = _gen(lambda mo, d: f"{MONTH_AK[mo]} {d}")


@pytest.mark.parametrize("text,mo,d", GEN_CASES)
def test_genitive_bare_rolls_future(text, mo, d):
    assert start(text) == ad(_rolled(mo, d))


@pytest.mark.parametrize("text,mo,d", AK_CASES)
def test_ak_bare_rolls_future(text, mo, d):
    assert start(text) == ad(_rolled(mo, d))


@pytest.mark.parametrize("text,mo,d", AK_CASES)
def test_ak_bare_span_one_day(text, mo, d):
    s, e = start_end(text)
    g = _rolled(mo, d)
    assert (s, e) == (ad(g), ad(g + timedelta(days=1)))
