# -*- coding: utf-8 -*-
"""Oracle sweep: من DAY0 MONTH0 YEAR0 إلى DAY1 MONTH1 YEAR1 -- an inclusive
range between two fully-specified civil dates.  Start is the first date; end is
exclusive at the day after the second date.  Both Gulf and Levantine month
names and both Western and Arabic-Indic digits.  Independent arithmetic gold."""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS, _arabic_indic as _ai

# (d0, m0, y0, d1, m1, y1)
SPANS = [
    (5, 1, 2019, 12, 3, 2019),
    (10, 4, 2018, 3, 5, 2018),
    (1, 1, 2000, 31, 12, 2000),
    (15, 6, 2021, 20, 9, 2021),
    (28, 2, 2016, 1, 3, 2016),
    (20, 7, 1969, 24, 7, 1969),
    (3, 11, 2022, 9, 11, 2022),
    (25, 12, 2020, 2, 1, 2021),
]


def _cases():
    out = []
    for d0, m0, y0, d1, m1, y1 in SPANS:
        s = date(y0, m0, d0)
        e = date(y1, m1, d1) + timedelta(days=1)
        g0, l0 = MONTHS[m0]
        g1, l1 = MONTHS[m1]
        out.append((f"من {d0} {g0} {y0} إلى {d1} {g1} {y1}", s, e))
        out.append((f"من {d0} {l0} {y0} إلى {d1} {l1} {y1}", s, e))
        out.append((
            f"من {_ai(d0)} {g0} {_ai(y0)} إلى {_ai(d1)} {g1} {_ai(y1)}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_full_date_range_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
