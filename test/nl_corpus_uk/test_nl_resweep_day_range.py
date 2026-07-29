# -*- coding: utf-8 -*-
"""Second-pass sweep: intra-month day ranges (uk), "з N по M" / "від N до M".

test_uk_day_range_year.py pins a single instance ("з 5 по 12 серпня 2019").
This sweep exercises both range markers ("з ... по ..." and "від ... до...")
across all 12 months and 5 fresh years (2028-2032), with day span 3-9 (valid
in every month, no month-length edge cases). The shared month/year token
must be lent to both endpoints; end is exclusive (day after M). Gold is
literal calendar arithmetic, independent of the parser. Anchor Tue
2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

_MONTHS_GEN = [
    None, "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]

_YEARS = (2028, 2029, 2030, 2031, 2032)

_TEMPLATES = [
    "з {d1} по {d2} {month} {y}",
    "від {d1} до {d2} {month} {y}",
]

_CASES = []
for _tmpl in _TEMPLATES:
    for _m in range(1, 13):
        for _y in _YEARS:
            _phrase = _tmpl.format(d1=3, d2=9, month=_MONTHS_GEN[_m], y=_y)
            _CASES.append((_phrase, _y, _m, 3, 9))


@pytest.mark.parametrize("phrase,y,m,d1,d2", _CASES)
def test_day_range_fresh(phrase, y, m, d1, d2):
    ss, ee = start_end(phrase)
    assert ss == AstroDate(y, m, d1), phrase
    assert ee == AstroDate(y, m, d2 + 1), phrase
    assert parse(phrase)[1] == "", phrase
