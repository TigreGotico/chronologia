# -*- coding: utf-8 -*-
"""Oracle sweep: full day-month-year dates (bg).

"5 март 2019" -- lit. "5 March 2019" -- resolves to that single calendar day,
the half-open span [date, date + 1 day).  Gold is the date itself; the year is
always explicit so nothing rolls.  Every emitted (day, month, year) is a real
calendar date (nonexistent days such as 31 April are filtered out).

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
    # day 15 across every month of 2019
    for m in range(1, 13):
        out.append((15, m, 2019))
    # varied days across a spread of months/years
    for d in (1, 7, 23, 28):
        for m in (1, 4, 8, 11):
            out.append((d, m, 2021))
    for d in (3, 11, 19, 25):
        for m in (2, 5, 9, 12):
            out.append((d, m, 2023))
    out.append((29, 2, 2020))   # leap day
    out.append((31, 12, 2030))
    out.append((30, 6, 2018))
    # keep only real dates, dedup
    seen, real = set(), []
    for d, m, y in out:
        if d <= calendar.monthrange(y, m)[1] and (d, m, y) not in seen:
            seen.add((d, m, y))
            real.append((d, m, y))
    return real


CASES = _cases()


@pytest.mark.parametrize("d,m,y", CASES,
                         ids=[f"{d} {MONTHS[m]} {y}" for d, m, y in CASES])
def test_full_date(d, m, y):
    phrase = f"{d} {MONTHS[m]} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, m, d), phrase
    nxt = date(y, m, d) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
