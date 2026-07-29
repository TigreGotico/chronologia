# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: من YEAR0 إلى YEAR1 -- inclusive whole-year
range, fresh pairs disjoint from ``test_nl_year_range_sweep``.  Start is
1 January of YEAR0; end is exclusive at 1 January of the year after YEAR1.
Western and Arabic-Indic digits.  Independent arithmetic gold."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import _arabic_indic as _ai

PAIRS = [
    (1952, 1959), (1963, 1968), (1977, 1982), (1988, 1996),
    (1993, 1994), (2002, 2011), (2006, 2008), (2015, 2019),
    (2021, 2025), (2030, 2036), (2038, 2045), (1946, 1950),
    (1971, 1980), (1959, 1961), (2044, 2049),
]


def _cases():
    out = []
    for y0, y1 in PAIRS:
        s = date(y0, 1, 1)
        e = date(y1 + 1, 1, 1)
        out.append((f"من {y0} إلى {y1}", s, e))
        out.append((f"من {_ai(y0)} إلى {_ai(y1)}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_year_range_resweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
