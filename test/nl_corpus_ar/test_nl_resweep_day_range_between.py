# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: بين DAY و DAY MONTH -- the "between" phrasing
of an inclusive intra-month day range (``test_nl_day_range_sweep`` only
exercises the من..إلى phrasing).  Same resolution rule: a bare month with no
year resolves to its next occurrence relative to the anchor (year kept if the
start day is still >= anchor, else rolled forward one year).  End is
exclusive (last day + 1).  Gold by independent arithmetic."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS

RANGES = [(2, 8), (14, 22), (4, 11), (6, 26)]


def _cases():
    anchor_d = ANCHOR.date()
    out = []
    for m, (gulf, lev) in MONTHS.items():
        for d0, d1 in RANGES:
            y = anchor_d.year
            if date(y, m, d0) < anchor_d:
                y += 1
            s = date(y, m, d0)
            e = date(y, m, d1) + timedelta(days=1)
            out.append((f"بين {d0} و {d1} {gulf}", s, e))
            out.append((f"بين {d0} و {d1} {lev}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_day_range_between_resweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
