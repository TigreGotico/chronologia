# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: من MONTH0 YEAR إلى MONTH1 YEAR -- inclusive
whole-month range with both endpoints carrying the same explicit year, over a
fresh set of years disjoint from ``test_nl_month_year_range_sweep``
(2020, 1996).  Every ordered month pair (m0 < m1), both Gulf and Levantine
naming.  Independent arithmetic gold."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS

YEARS = (2003, 2031, 1974, 1959)


def _end(y, m1):
    return date(y + 1, 1, 1) if m1 == 12 else date(y, m1 + 1, 1)


def _cases():
    out = []
    for y in YEARS:
        for m0 in range(1, 13):
            for m1 in range(m0 + 1, 13):
                s = date(y, m0, 1)
                e = _end(y, m1)
                for names in zip(MONTHS[m0], MONTHS[m1]):
                    out.append(
                        (f"من {names[0]} {y} إلى {names[1]} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_year_range_resweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
