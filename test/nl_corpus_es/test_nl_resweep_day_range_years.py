# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: "del N al M de <month> de <year>" day-ranges with an
EXPLICIT trailing year, across a month x year matrix.

``test_nl_ranges.py`` proves the shared-month-name range form and its
prefer-future roll without an explicit year; this file pins the explicit-year
tail so every month is exercised with a fixed, unambiguous year (no roll
needed, since the year removes any past/future ambiguity).

Gold: start = (year, month, N); end = day after M, i.e. (year, month, M+1),
verified never to cross a month boundary for the day pairs used here.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS = [
    ("enero", 1), ("febrero", 2), ("marzo", 3), ("abril", 4),
    ("mayo", 5), ("junio", 6), ("julio", 7), ("agosto", 8),
    ("septiembre", 9), ("octubre", 10), ("noviembre", 11), ("diciembre", 12),
]
_YEARS = [2016, 2019, 2021, 2024, 2028]
_DAY_PAIRS = [(5, 12), (15, 20)]


def _cases():
    out = []
    for mn, m in _MONTHS:
        for y in _YEARS:
            for n, mm in _DAY_PAIRS:
                text = f"del {n} al {mm} de {mn} de {y}"
                out.append((text, (y, m, n), (y, m, mm + 1)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_day_range_with_explicit_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s), f"{text!r} start {ss} != {s}"
    assert ee == AstroDate(*e), f"{text!r} end {ee} != {e}"
