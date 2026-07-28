# -*- coding: utf-8 -*-
"""Oracle sweep: من MONTH0 YEAR إلى MONTH1 YEAR -- an inclusive whole-month range
with both endpoints carrying the same explicit year.  Start is the first of
MONTH0 of that year; end is exclusive at the first of the month after MONTH1
(rolling into next January when MONTH1 is December).  Every ordered month pair
(m0 < m1), both Gulf and Levantine naming, across two years.  Independent
arithmetic gold."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS


def _end(y, m1):
    return date(y + 1, 1, 1) if m1 == 12 else date(y, m1 + 1, 1)


def _cases():
    out = []
    for y in (2020, 1996):
        for m0 in range(1, 13):
            for m1 in range(m0 + 1, 13):
                s = date(y, m0, 1)
                e = _end(y, m1)
                for names in zip(MONTHS[m0], MONTHS[m1]):
                    out.append(
                        (f"من {names[0]} {y} إلى {names[1]} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_year_range_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
