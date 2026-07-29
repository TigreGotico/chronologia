# -*- coding: utf-8 -*-
"""da (second-pass resweep): "den N. <weekday> i <month> <year>" and
"sidste <weekday> i <month> <year>" -- fresh months and fresh years not
exercised by ``test_da_ordinal_weekday.py`` (which sticks to marts/juni/
september/november 2019-2021).

Gold is independent calendar arithmetic: find the month's first matching
weekday, then step whole weeks (or walk back from the month's last day for
"sidste"). Both are resolved by the parser (see ``test_last_weekday_of_month``
in the sibling file), so no xfail is expected here.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, AstroDate

_WD = {"mandag": 0, "tirsdag": 1, "onsdag": 2, "torsdag": 3,
       "fredag": 4, "lørdag": 5, "søndag": 6}
# fresh months -- the sibling file only covers marts/juni/september/november
_MONTHS = {1: "januar", 2: "februar", 4: "april", 7: "juli",
           8: "august", 10: "oktober"}
_ORD = [("første", 1), ("anden", 2), ("tredje", 3), ("fjerde", 4)]
_YEARS = (2028, 2031, 2034, 2037)


def _nth_weekday(y, m, wd, n):
    first = date(y, m, 1)
    offset = (wd - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


def _last_weekday(y, m, wd):
    if m == 12:
        last = date(y, 12, 31)
    else:
        last = date(y, m + 1, 1) - timedelta(days=1)
    offset = (last.weekday() - wd) % 7
    return last - timedelta(days=offset)


_NTH_CASES = []
for _ordw, _n in _ORD:
    for _wdname, _wd in _WD.items():
        for _m, _mname in _MONTHS.items():
            for _y in _YEARS:
                _exp = _nth_weekday(_y, _m, _wd, _n)
                _NTH_CASES.append(
                    (f"den {_ordw} {_wdname} i {_mname} {_y}", _exp))


@pytest.mark.parametrize("text,exp", _NTH_CASES)
def test_nth_weekday_of_month_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


_LAST_CASES = []
for _wdname, _wd in _WD.items():
    for _m, _mname in _MONTHS.items():
        for _y in _YEARS:
            _exp = _last_weekday(_y, _m, _wd)
            _LAST_CASES.append((f"sidste {_wdname} i {_mname} {_y}", _exp))


@pytest.mark.parametrize("text,exp", _LAST_CASES)
def test_last_weekday_of_month_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)
