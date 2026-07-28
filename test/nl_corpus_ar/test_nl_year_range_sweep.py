# -*- coding: utf-8 -*-
"""Oracle sweep: من YEAR0 إلى YEAR1 -- an inclusive whole-year range.  Start is
1 January of YEAR0; end is exclusive at 1 January of the year after YEAR1.
Exercised in both Western and Arabic-Indic (٠-٩) digits.  Independent
arithmetic gold."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import _arabic_indic as _ai

PAIRS = [
    (2010, 2015), (1990, 2000), (2000, 2020), (1985, 1999),
    (2018, 2027), (1948, 1967), (2001, 2003), (1975, 1985),
    (1999, 2001), (2012, 2013), (1969, 1970), (2033, 2040),
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
def test_year_range_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
