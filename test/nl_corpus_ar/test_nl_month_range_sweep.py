# -*- coding: utf-8 -*-
"""Oracle sweep: من MONTH0 إلى MONTH1 -- an inclusive whole-month range.  With
no year given both endpoints resolve inside the anchor's own year (no forward
roll): start is the first of MONTH0, end is exclusive at the first of the month
after MONTH1 (spilling into next January when MONTH1 is December).  Exercised
over every ordered month pair (m0 < m1) in both the Gulf and Levantine naming
systems.  Gold by independent arithmetic against the Tue 2017-06-27 anchor."""
from datetime import date

import pytest

from ._corpus import ANCHOR, AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS


def _end(m1):
    y = ANCHOR.year
    return date(y + 1, 1, 1) if m1 == 12 else date(y, m1 + 1, 1)


def _cases():
    out = []
    for m0 in range(1, 13):
        for m1 in range(m0 + 1, 13):
            s = date(ANCHOR.year, m0, 1)
            e = _end(m1)
            for names in zip(MONTHS[m0], MONTHS[m1]):  # (gulf,gulf) then (lev,lev)
                out.append((f"من {names[0]} إلى {names[1]}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_range_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
