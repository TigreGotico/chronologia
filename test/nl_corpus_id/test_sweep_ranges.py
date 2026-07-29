# -*- coding: utf-8 -*-
"""Oracle sweep: closed day ranges within a named month, stated with an explicit
year so the fold is fixed.

Indonesian frames these as ``d1 sampai d2 Bulan YYYY`` (inclusive "until"),
``dari d1 sampai d2 Bulan YYYY``, and the dash form ``d1-d2 Bulan YYYY``. A
closed range covers whole civil days, so gold is [d1 00:00, (d2+1) 00:00) --
the terminator day is part of the period (KBBI s.v. "sampai" sense 6). Gold by
independent arithmetic; anchor fixed but irrelevant given explicit years.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

A = datetime(2017, 6, 27, 13, 4)

MON = ("Januari Februari Maret April Mei Juni Juli Agustus September "
       "Oktober November Desember").split()


def _cases():
    out = []
    for y in (2019, 2020):
        for m in range(1, 13):
            mn = MON[m - 1]
            for d1, d2 in ((5, 12), (1, 15)):
                end = date(y, m, d2) + timedelta(days=1)
                gs = AstroDate(y, m, d1)
                ge = AstroDate(end.year, end.month, end.day)
                for text in (f"{d1} sampai {d2} {mn} {y}",
                             f"{d1}-{d2} {mn} {y}"):
                    out.append((text, gs, ge))
            # one "dari ... sampai" phrasing per month for variety
            end = date(y, m, 20) + timedelta(days=1)
            out.append((f"dari 10 sampai 20 {mn} {y}",
                        AstroDate(y, m, 10),
                        AstroDate(end.year, end.month, end.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_closed_day_range_in_month(text, s, e):
    assert start_end(text, A) == (s, e)


# -- cross-month closed ranges, both endpoints carrying the same explicit year
def _cross():
    out = []
    for y in (2019, 2020):
        for m1, d1, m2, d2 in ((6, 28, 7, 3), (1, 15, 2, 10), (11, 20, 12, 5)):
            end = date(y, m2, d2) + timedelta(days=1)
            out.append((f"{d1} {MON[m1 - 1]} {y} sampai {d2} {MON[m2 - 1]} {y}",
                        AstroDate(y, m1, d1),
                        AstroDate(end.year, end.month, end.day)))
    return out


@pytest.mark.parametrize("text,s,e", _cross())
def test_closed_range_crosses_month(text, s, e):
    assert start_end(text, A) == (s, e)
