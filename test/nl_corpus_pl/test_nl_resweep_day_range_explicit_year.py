# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: Polish intra-month day ranges "od N do M
MONTH(gen) YEAR" with an EXPLICIT year, swept across fresh day pairs and all
twelve months. ``test_pl_day_range_sweep.py`` covers pairs (5,12)/(3,20)/
(1,15)/(10,25) with an IMPLIED year (derived by walking forward from the
anchor); this module uses different day pairs and pins the year explicitly in
the phrase itself, so the expected year is simply the literal year typed.

"od 8 do 20 lipca 2019" is the closed day range 8..20 of July 2019, a span
[2019-07-08 00:00, 2019-07-21 00:00). Every expected value is pure calendar
arithmetic; the parser is never consulted for gold.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span

_MON = [
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
    "lipca", "sierpnia", "września", "października", "listopada", "grudnia",
]
#: fresh day pairs -- disjoint from the first-pass (5,12)/(3,20)/(1,15)/(10,25).
_PAIRS = [(2, 9), (8, 20), (14, 28), (6, 17), (11, 22)]
#: fresh explicit years -- disjoint from the anchor-forward years the
#: first-pass sweep resolves to (which start at 2017/2018).
_YEARS = (2013, 2019, 2024, 2029)


def _cases():
    out = []
    for y in _YEARS:
        for a, b in _PAIRS:
            for mi, mon in enumerate(_MON, 1):
                gs = AstroDate(y, mi, a)
                ge_d = date(y, mi, b) + timedelta(days=1)
                ge = AstroDate(ge_d.year, ge_d.month, ge_d.day)
                out.append((f"od {a} do {b} {mon} {y}", gs, ge))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gs,ge", _CASES, ids=[c[0] for c in _CASES])
def test_day_range_explicit_year(text, gs, ge):
    s = span(text)
    assert (s.start, s.end) == (gs, ge)
