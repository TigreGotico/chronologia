# -*- coding: utf-8 -*-
"""Oracle sweep: ``Bulan YYYY`` -> the whole named month.

Gold: [first-of-month 00:00, first-of-next-month 00:00). Independent arithmetic
(month rollover via day-32 normalisation). Anchor-independent (explicit year).
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()


def _cases():
    out = []
    for y in (1945, 1990, 2000, 2010, 2019, 2020, 2027, 2030):
        for m in range(1, 13):
            nm = (date(y, m, 1) + timedelta(days=32)).replace(day=1)
            out.append((f"{MON[m - 1]} {y}",
                        AstroDate(y, m, 1),
                        AstroDate(nm.year, nm.month, 1)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_year_whole_month(text, s, e):
    assert start_end(text) == (s, e)
