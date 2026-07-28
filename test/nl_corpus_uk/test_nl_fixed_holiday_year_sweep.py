# -*- coding: utf-8 -*-
"""Fixed-date feast + explicit-year sweep (uk).

These feasts sit on a fixed calendar day every year, so "<feast> <year>" must
resolve to that exact day.  This locale's community keeps the Julian nativity
cycle, so Різдво is 7 January and Святвечір is 6 January (cross-checked against
the bare-holiday golds in test_nl_holiday_ref.py).  Each date is tabulated
independently of the parser.  Anchor Tue 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, span, start

# feast surface -> (month, day)
_FIXED = {
    "новий рік": (1, 1),
    "різдво": (1, 7),
    "святвечір": (1, 6),
    "день святого валентина": (2, 14),
    "гелловін": (10, 31),
}

_YEARS = range(2018, 2028)

_CASES = []
for _name, (_m, _d) in _FIXED.items():
    for _y in _YEARS:
        _CASES.append((f"{_name} {_y}", _y, _m, _d))


@pytest.mark.parametrize("phrase,y,m,d", _CASES)
def test_fixed_feast_with_year(phrase, y, m, d):
    assert start(phrase) == AstroDate(y, m, d), phrase
    assert span(phrase).width == timedelta(days=1), phrase
