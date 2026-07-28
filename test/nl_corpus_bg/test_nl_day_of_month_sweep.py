# -*- coding: utf-8 -*-
"""Oracle sweep: bare day-of-month with no year rolls to the next occurrence
(bg).

"5 март" carries no year, so it resolves to the first day-month on or after the
anchor date: if (month, day) >= (anchor.month, anchor.day) it stays in the
anchor year, otherwise it rolls to the next year.  Gold applies that rule with
independent arithmetic; the parser is never consulted.

Anchor 2017-06-27 (Tuesday, 13:04) -- so 27 June is the roll boundary.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

MONTHS = ["", "януари", "февруари", "март", "април", "май", "юни", "юли",
          "август", "септември", "октомври", "ноември", "декември"]
ANCHOR = date(2017, 6, 27)


def _roll(m, d):
    y = ANCHOR.year if (m, d) >= (ANCHOR.month, ANCHOR.day) else ANCHOR.year + 1
    return date(y, m, d)


def _cases():
    out = []
    for m in (1, 3, 6, 9, 12):
        for d in (3, 9, 14, 20, 28):
            if d <= calendar.monthrange(2017, m)[1]:
                out.append((m, d))
    return out


CASES = _cases()


@pytest.mark.parametrize("m,d", CASES, ids=[f"{d} {MONTHS[m]}" for m, d in CASES])
def test_day_of_month_rolls_forward(m, d):
    phrase = f"{d} {MONTHS[m]}"
    gold = _roll(m, d)
    s = span(phrase)
    assert s.start == AstroDate(gold.year, gold.month, gold.day), phrase
    nxt = gold + timedelta(days=1)
    assert s.end == AstroDate(nxt.year, nxt.month, nxt.day), phrase
