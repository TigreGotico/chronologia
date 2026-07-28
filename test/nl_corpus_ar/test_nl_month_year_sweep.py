# -*- coding: utf-8 -*-
"""Oracle sweep: MONTH YEAR -> whole civil month [Y-M-01, next-month-01).
All twelve months in both Gulf and Levantine naming, independent arithmetic."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end
from .test_nl_full_date_sweep import MONTHS


def _next_month(y, m):
    return (y + 1, 1) if m == 12 else (y, m + 1)


def _cases():
    out = []
    for m, (gulf, lev) in MONTHS.items():
        for y in (2020, 1985):
            ny, nm = _next_month(y, m)
            s = date(y, m, 1)
            e = date(ny, nm, 1)
            for name in (gulf, lev):
                out.append((f"{name} {y}", s, e))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_month_year_sweep(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(s.year, s.month, s.day)
    assert ee == AstroDate(e.year, e.month, e.day)
