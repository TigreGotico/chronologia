# -*- coding: utf-8 -*-
"""Second-pass oracle sweep: closed day ranges within one month (bg), FRESH
day-pairs/months/years disjoint from test_nl_range_sweep.py.

"от 2 до 9 март 2018" -- lit. "from 2 to 9 March 2018" -- spans the inclusive
day range, i.e. the half-open span [start-day, end-day + 1 day). Gold is
that arithmetic with an explicit year (deterministic).

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]


def _cases():
    out = []
    for d1, d2 in ((2, 9), (6, 14), (11, 22), (20, 27)):
        for m in (2, 3, 5, 6, 8, 9, 10, 12):
            for y in (2018, 2020, 2022, 2024):
                if d2 <= calendar.monthrange(y, m)[1]:
                    out.append((d1, d2, m, y))
    return out


CASES = _cases()


@pytest.mark.parametrize("d1,d2,m,y", CASES,
                         ids=[f"от {d1} до {d2} {MONTHS[m]} {y}"
                              for d1, d2, m, y in CASES])
def test_range_explicit_year_resweep(d1, d2, m, y):
    phrase = f"от {d1} до {d2} {MONTHS[m]} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, m, d1), phrase
    nxt = date(y, m, d2) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
