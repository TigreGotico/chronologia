# -*- coding: utf-8 -*-
"""da: "den N. <weekday> i <month> <year>" -- the Nth weekday of a month.

The gold day is computed by independent calendar arithmetic (find the first
weekday of the month, then step whole weeks); it is never read back from the
parser.  Both spelled ordinals ("anden") and numeric ones ("2.") fold to the
same day, and the connector is the native "i".  n is kept to 1..4 so the
target weekday always exists in every month.

"sidste <weekday> i <month>" (the *last* weekday) is not yet resolved -- the
parser strands it back onto the anchor -- so it is pinned xfail, never with a
wrong gold.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, nomatch, AstroDate

_WD = {"mandag": 0, "tirsdag": 1, "onsdag": 2, "torsdag": 3,
       "fredag": 4, "lørdag": 5, "søndag": 6}
_MONTHS = {3: "marts", 6: "juni", 9: "september", 11: "november"}
_ORD = [("første", 1), ("anden", 2), ("tredje", 3), ("fjerde", 4),
        ("1.", 1), ("2.", 2), ("3.", 3), ("4.", 4)]
_YEARS = (2019, 2020, 2021)


def _nth_weekday(y, m, wd, n):
    first = date(y, m, 1)
    offset = (wd - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


_CASES = []
for _ordw, _n in _ORD:
    for _wdname, _wd in _WD.items():
        for _m, _mname in _MONTHS.items():
            for _y in _YEARS:
                _exp = _nth_weekday(_y, _m, _wd, _n)
                _CASES.append((f"{_ordw} {_wdname} i {_mname} {_y}", _exp))


@pytest.mark.parametrize("text,exp", _CASES)
def test_ordinal_weekday_of_month(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.xfail(strict=True, reason="'sidste <weekday> i <month>' not "
                   "resolved: parser strands the phrase back onto the anchor")
@pytest.mark.parametrize("text,exp", [
    ("sidste mandag i marts 2020", date(2020, 3, 30)),
    ("sidste fredag i maj 2021", date(2021, 5, 28)),
    ("sidste søndag i november 2019", date(2019, 11, 24)),
])
def test_last_weekday_of_month_xfail(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
