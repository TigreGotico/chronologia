# -*- coding: utf-8 -*-
"""da (second-pass resweep): day ranges, fresh months/years plus a
cross-month shape not covered by ``test_da_ranges_sweep.py`` (which sticks
to marts/maj/juni/august/oktober and same-month spans).

Same-month explicit-year ranges: "fra D1. til D2. <month> <year>".
Cross-month explicit-year ranges: "fra D1. <month1> til D2. <month2> <year>".

The range end is exclusive: the last named day plus one. Gold is arithmetic,
never read from the parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start_end, AstroDate

# fresh months -- the sibling sweep only covers marts/maj/juni/august/oktober
_MONTHS = {1: "januar", 2: "februar", 4: "april", 7: "juli",
           9: "september", 11: "november"}
_PAIRS = [(1, 5), (3, 9), (5, 12), (10, 20), (12, 25), (2, 28)]
_YEARS = (2028, 2030, 2032, 2034)

_SAME_MONTH = []
for _m, _mname in _MONTHS.items():
    for _yr in _YEARS:
        for _d1, _d2 in _PAIRS:
            _s = AstroDate(_yr, _m, _d1)
            _e = AstroDate(_yr, _m, _d2) + timedelta(days=1)
            _SAME_MONTH.append(
                (f"fra {_d1}. til {_d2}. {_mname} {_yr}", _s, _e))


@pytest.mark.parametrize("text,s,e", _SAME_MONTH)
def test_same_month_range_fresh(text, s, e):
    assert start_end(text) == (s, e)


# cross-month day ranges: "fra 5. januar til 12. februar 2028"
_MONTH_SEQ = list(_MONTHS.items())
_CROSS = []
for _i in range(len(_MONTH_SEQ) - 1):
    _m1, _n1 = _MONTH_SEQ[_i]
    _m2, _n2 = _MONTH_SEQ[_i + 1]
    for _yr in _YEARS:
        _d1, _d2 = 20, 12  # 20th of month1 through 12th of month2
        _s = AstroDate(_yr, _m1, _d1)
        _end_date = date(_yr, _m2, _d2) + timedelta(days=1)
        _e = AstroDate(_end_date.year, _end_date.month, _end_date.day)
        _CROSS.append(
            (f"fra {_d1}. {_n1} til {_d2}. {_n2} {_yr}", _s, _e))


@pytest.mark.parametrize("text,s,e", _CROSS)
def test_cross_month_range_fresh(text, s, e):
    assert start_end(text) == (s, e)
