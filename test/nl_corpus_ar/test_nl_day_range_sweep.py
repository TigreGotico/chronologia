# -*- coding: utf-8 -*-
"""Oracle sweep: من DAY إلى DAY MONTH -- an inclusive intra-month day range.
The bare month (no year) resolves to its next occurrence: the year is kept if
the start day still lies on or after the anchor date, else rolled forward one
year.  End is exclusive (last day + 1).  Gold by independent arithmetic."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, start_end

MONTHS = {
    1: "يناير", 2: "فبراير", 3: "مارس", 6: "يونيو",
    9: "سبتمبر", 10: "أكتوبر", 12: "ديسمبر",
}

RANGES = [(5, 12), (1, 10), (10, 20), (3, 9)]


def _cases():
    anchor_d = ANCHOR.date()
    out = []
    for m, name in MONTHS.items():
        for d0, d1 in RANGES:
            y = anchor_d.year
            if date(y, m, d0) < anchor_d:
                y += 1
            s = date(y, m, d0)
            e = date(y, m, d1) + timedelta(days=1)
            out.append((f"من {d0} إلى {d1} {name}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_day_range_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
