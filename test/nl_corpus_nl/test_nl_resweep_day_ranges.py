# -*- coding: utf-8 -*-
"""Second-pass resweep: within-month day ranges with explicit year (nl).

"van <d1> tot <d2> <maand> <jaar>". :mod:`test_nl_range_sweep` exercises this
shape only with a bare (implicit next-occurrence) year; this file pins an
explicit year instead, over fresh years 2029-2033. Semantics: the range
covers [d1, d2] of the named month and the end edge is d2 + 1 day. Gold is
computed here, independent of the parser.

Anchor: Tuesday 2017-06-27 13:04.
"""
import calendar
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

_MONTHS = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
_YEARS = [2029, 2030, 2031, 2032, 2033]
_DAY_PAIRS = [(2, 8), (4, 11), (9, 19), (14, 24)]


def _build():
    cases = []
    for y in _YEARS:
        for mi, mname in enumerate(_MONTHS, start=1):
            last = calendar.monthrange(y, mi)[1]
            for d1, d2 in _DAY_PAIRS:
                if d2 > last:
                    continue
                s = date(y, mi, d1)
                e = date(y, mi, d2) + timedelta(days=1)
                cases.append((f"van {d1} tot {d2} {mname} {y}", s, e))
    return cases


_CASES = _build()


@pytest.mark.parametrize("phrase,s,e", _CASES, ids=[c[0] for c in _CASES])
def test_within_month_range_explicit_year(phrase, s, e):
    assert start_end(phrase) == (
        AstroDate(s.year, s.month, s.day),
        AstroDate(e.year, e.month, e.day),
    ), phrase
