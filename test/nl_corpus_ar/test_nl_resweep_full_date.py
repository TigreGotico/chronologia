# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: DAY MONTH YEAR with a fresh set of (day, year)
pairs not exercised by ``test_nl_full_date_sweep``, across all twelve months
in both the Gulf (يناير..) and Levantine (كانون الثاني..) naming systems,
plus Arabic-Indic digits.  Gold is a single civil day [Y-M-D, Y-M-D+1)
derived by independent stdlib arithmetic, never the parser."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS, _arabic_indic

# fresh (day, year) pairs, disjoint from the original sweep's DAY_YEARS
# ((3,2019),(15,2020),(28,1999),(1,2033),(22,1948)); kept <=28 so every
# month accepts every day.
DAY_YEARS = [
    (7, 2011), (19, 2016), (25, 2004), (2, 2044), (11, 1977),
    (17, 1990), (28, 2050), (9, 1962), (23, 2029), (5, 1955),
    (14, 2038), (21, 1983), (4, 2001), (26, 1971), (12, 2022),
    (8, 2007), (16, 1999),
]


def _cases():
    out = []
    for m, (gulf, lev) in MONTHS.items():
        for d, y in DAY_YEARS:
            s = date(y, m, d)
            e = s + timedelta(days=1)
            for name in (gulf, lev):
                out.append((f"{d} {name} {y}", s, e))
            out.append((f"{_arabic_indic(d)} {lev} {_arabic_indic(y)}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_full_date_resweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
