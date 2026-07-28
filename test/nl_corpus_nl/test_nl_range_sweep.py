# -*- coding: utf-8 -*-
"""Bare within-month range sweep (nl): "van <d1> tot <d2> <maand>".

Semantics confirmed by probing: the range covers [d1, d2] of the named month
and the end edge is d2 + 1 day (the day after the last named day). With no
explicit year the month resolves to its next occurrence on/after the anchor
(2017-06-27): months July..December fall in 2017, January..May in 2018. June
is skipped as it straddles the anchor and its roll direction is day-dependent.

Gold years and edges are computed here, independent of the parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

# month name -> (index, resolved year under next-occurrence from 2017-06-27)
_MONTHS = [
    ("juli", 7, 2017), ("augustus", 8, 2017), ("september", 9, 2017),
    ("oktober", 10, 2017), ("november", 11, 2017), ("december", 12, 2017),
    ("januari", 1, 2018), ("februari", 2, 2018), ("maart", 3, 2018),
    ("april", 4, 2018), ("mei", 5, 2018),
]
_DAY_PAIRS = [(3, 9), (5, 12), (10, 20), (1, 15)]


def _build():
    cases = []
    for mname, mi, y in _MONTHS:
        for d1, d2 in _DAY_PAIRS:
            s = date(y, mi, d1)
            e = date(y, mi, d2) + timedelta(days=1)
            cases.append((f"van {d1} tot {d2} {mname}", s, e))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,s,e", _CASES, ids=[c[0] for c in _CASES])
def test_within_month_range(phrase, s, e):
    assert start_end(phrase) == (
        AstroDate(s.year, s.month, s.day),
        AstroDate(e.year, e.month, e.day),
    ), phrase
