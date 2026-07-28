# -*- coding: utf-8 -*-
"""Polish intra-month day ranges "od N do M MONTH(gen)", swept across day pairs
and all twelve months.

"od 5 do 12 czerwca" is the closed day range 5..12 of that month, a span
[day N 00:00, day M+1 00:00).  With no explicit year the engine picks the next
future occurrence relative to the anchor; the expected year is derived here
independently by walking forward from 2017 to the first year whose start day is
strictly after the anchor date.  The parser is never consulted for gold.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span

_MON = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia",
]
_PAIRS = [(5, 12), (3, 20), (1, 15), (10, 25)]


def _year(month, day):
    y = 2017
    while not (date(y, month, day) > ANCHOR.date()):
        y += 1
    return y


def _cases():
    out = []
    for a, b in _PAIRS:
        for mi, mon in enumerate(_MON, 1):
            y = _year(mi, a)
            gs = AstroDate(y, mi, a)
            ge_d = date(y, mi, b) + timedelta(days=1)
            ge = AstroDate(ge_d.year, ge_d.month, ge_d.day)
            out.append((f"od {a} do {b} {mon}", gs, ge))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_day_range(text, gs, ge):
    s = span(text)
    assert (s.start, s.end) == (gs, ge)
