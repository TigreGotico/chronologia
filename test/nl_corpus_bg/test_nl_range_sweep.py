# -*- coding: utf-8 -*-
"""Oracle sweep: closed day ranges within one month (bg).

"от 5 до 12 юни 2018" -- lit. "from 5 to 12 June 2018" -- spans the inclusive
day range, i.e. the half-open span [start-day, end-day + 1 day).  Gold is that
arithmetic with an explicit year (deterministic).  A small no-year block checks
the roll-forward rule (start-day anchored like a bare date).

Anchor 2017-06-27 (Tuesday, 13:04).
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
ANCHOR = date(2017, 6, 27)


def _cases():
    out = []
    for d1, d2 in ((5, 12), (1, 10), (3, 20), (15, 28)):
        for m in (1, 4, 7, 11):
            for y in (2019, 2021):
                if d2 <= calendar.monthrange(y, m)[1]:
                    out.append((d1, d2, m, y))
    return out


CASES = _cases()


@pytest.mark.parametrize("d1,d2,m,y", CASES,
                         ids=[f"от {d1} до {d2} {MONTHS[m]} {y}"
                              for d1, d2, m, y in CASES])
def test_range_explicit_year(d1, d2, m, y):
    phrase = f"от {d1} до {d2} {MONTHS[m]} {y}"
    s = span(phrase)
    assert s.start == AstroDate(y, m, d1), phrase
    nxt = date(y, m, d2) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase


_NOYEAR = [(5, 12, 6), (1, 5, 1), (10, 20, 3), (2, 8, 12)]


@pytest.mark.parametrize("d1,d2,m", _NOYEAR,
                         ids=[f"от {d1} до {d2} {MONTHS[m]}"
                              for d1, d2, m in _NOYEAR])
def test_range_rolls_forward(d1, d2, m):
    phrase = f"от {d1} до {d2} {MONTHS[m]}"
    y = ANCHOR.year if (m, d1) >= (ANCHOR.month, ANCHOR.day) else ANCHOR.year + 1
    s = span(phrase)
    assert s.start == AstroDate(y, m, d1), phrase
    nxt = date(y, m, d2) + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
