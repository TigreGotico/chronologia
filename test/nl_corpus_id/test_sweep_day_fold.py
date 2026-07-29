# -*- coding: utf-8 -*-
"""Oracle sweep: yearless ``D Bulan`` folds to the next occurrence on or after
the anchor day.

Anchor is the mission Tuesday 2017-06-27 13:04. Fold rule (verified against the
existing calendar corpus): the year is the anchor year if that day is >= the
anchor date, else the following year. Gold by independent arithmetic.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

A = datetime(2017, 6, 27, 13, 4)
_AD = A.date()

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()


def _fold(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


def _cases():
    out = []
    for m in range(1, 13):
        for d in (1, 10, 20, 28):
            y = _fold(m, d)
            nxt = date(y, m, d) + timedelta(days=1)
            out.append((f"{d} {MON[m - 1]}",
                        AstroDate(y, m, d),
                        AstroDate(nxt.year, nxt.month, nxt.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_yearless_day_folds_forward(text, s, e):
    assert start_end(text, A) == (s, e)
