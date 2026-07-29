# -*- coding: utf-8 -*-
"""Second-pass sweep: Ukrainian civil holidays x explicit year (fresh years).

test_nl_fixed_holiday_year_sweep.py already covers Новий рік / Різдво /
Святвечір / Valentine / Halloween for 2018-2027, and
test_nl_national_holidays_2.py pins the movable-name civil holidays for
2017-2019 (bare) plus a couple of explicit 2019 years. This sweep exercises
ALL eight holidays named in the task brief over fresh years 2028-2047 that no
earlier file touches, closing the year-coverage gap. Every date is a fixed
Gregorian civil date (statutory, non-Easter-linked) verified independently of
the parser. Anchor Tue 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

# holiday surface -> (month, day)
_HOLIDAYS = {
    "новий рік": (1, 1),
    "різдво": (1, 7),
    "міжнародний жіночий день": (3, 8),
    "день праці": (5, 1),
    "день перемоги": (5, 9),
    "день конституції": (6, 28),
    "день незалежності": (8, 24),
    "день захисника": (10, 14),
}

_YEARS = range(2028, 2048)

_CASES = []
for _name, (_m, _d) in _HOLIDAYS.items():
    for _y in _YEARS:
        _CASES.append((f"{_name} {_y}", _y, _m, _d))


@pytest.mark.parametrize("phrase,y,m,d", _CASES)
def test_holiday_with_fresh_year(phrase, y, m, d):
    assert start(phrase) == AstroDate(y, m, d), phrase
    assert span(phrase).width == timedelta(days=1), phrase
