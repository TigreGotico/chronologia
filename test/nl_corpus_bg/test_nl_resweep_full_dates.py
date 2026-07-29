# -*- coding: utf-8 -*-
"""Second-pass oracle sweep: full day-month-year dates (bg), FRESH
day/month/year combos disjoint from test_nl_full_dates_sweep.py.

"9 март 2022" -- lit. "9 March 2022" -- resolves to that single calendar
day, the half-open span [date, date + 1 day). Gold is the date itself; the
year is always explicit so nothing rolls. Nonexistent days are filtered out.

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
    # day 9 across every month of 2022
    for m in range(1, 13):
        out.append((9, m, 2022))
    # varied days across a spread of months/years, disjoint from the
    # original sweep's (d, m, y) picks
    for d in (2, 14, 20):
        for m in (3, 6, 10):
            out.append((d, m, 2025))
    for d in (4, 16, 22):
        for m in (1, 7, 11):
            out.append((d, m, 2027))
    out.append((29, 2, 2028))   # leap day
    out.append((30, 4, 2019))
    out.append((31, 3, 2026))
    seen, real = set(), []
    for d, m, y in out:
        if d <= calendar.monthrange(y, m)[1] and (d, m, y) not in seen:
            seen.add((d, m, y))
            real.append((d, m, y))
    return real


CASES = _cases()


@pytest.mark.parametrize("d,m,y", CASES,
                         ids=[f"{d} {MONTHS[m]} {y}" for d, m, y in CASES])
def test_full_date_resweep(d, m, y):
    phrase = f"{d} {MONTHS[m]} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, m, d), phrase
    nxt = date(y, m, d) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
