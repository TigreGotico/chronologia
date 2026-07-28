# -*- coding: utf-8 -*-
"""Explicit day-month-year sweep (uk): "D <month>(gen) YYYY" -> that exact day.

Ukrainian dates run day-month-year with a genitive month name.  The gold is the
literal calendar date named in the phrase -- correct by construction, derived
without touching the parser.  Days are held at <=28 so every (day, month) pair
is valid in every year.  Anchor Tue 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse

_MONTHS_GEN = [
    None, "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]

_DAYS = (1, 8, 15, 23, 28)
_YEARS = (1991, 2018, 2020, 2024)

_CASES = []
for _m in range(1, 13):
    for _d in _DAYS:
        for _y in _YEARS:
            _CASES.append((f"{_d} {_MONTHS_GEN[_m]} {_y}", _y, _m, _d))


@pytest.mark.parametrize("phrase,y,m,d", _CASES)
def test_full_date(phrase, y, m, d):
    r = parse(phrase)
    assert r[0].start == AstroDate(y, m, d), phrase
    assert r[0].width == timedelta(days=1), phrase
