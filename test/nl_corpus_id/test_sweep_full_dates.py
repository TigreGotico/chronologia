# -*- coding: utf-8 -*-
"""Oracle sweep: every calendar day of 2019 (common) and 2020 (leap) as an
explicit Indonesian ``D Bulan YYYY`` date.

Gold is the calendar identity -- a full date names a single civil day, so the
span runs [that day 00:00, next day 00:00). Computed by independent arithmetic
(``datetime.date`` + ``timedelta``), never from the parser. Anchor is the
mission Tuesday 2017-06-27 13:04, irrelevant here because the year is explicit.
"""
from datetime import date, timedelta

import calendar
import pytest

from ._corpus import AstroDate, start_end

A = None  # explicit years -> anchor-independent; corpus default anchor is fine.

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()


def _cases():
    out = []
    for y in (2019, 2020):
        for m in range(1, 13):
            for d in range(1, calendar.monthrange(y, m)[1] + 1):
                nxt = date(y, m, d) + timedelta(days=1)
                out.append((f"{d} {MON[m - 1]} {y}",
                            AstroDate(y, m, d),
                            AstroDate(nxt.year, nxt.month, nxt.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_full_date_single_day(text, s, e):
    assert start_end(text) == (s, e)
