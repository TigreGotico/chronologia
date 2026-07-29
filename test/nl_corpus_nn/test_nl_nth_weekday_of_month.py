# -*- coding: utf-8 -*-
"""nn: "<ordinal> <weekday> i <month> <year>" -- the Nth weekday of a month,
and "siste <weekday> i <month> <year>" -- the last weekday of a month.

Nynorsk scopes the ordinal/last weekday against the named month with the native
connector "i" ("første måndag i januar 2020").  The gold day is computed by
independent calendar arithmetic and is never read back from the parser.  n is
kept to 1..4 so the target weekday always exists in every month.

A BARE "siste <weekday>" with NO trailing month stays anchor-relative
(weekday_ref); only the month-scoped form nests into scoped_ordinal.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, AstroDate, ANCHOR

_WD = {"måndag": 0, "onsdag": 2, "fredag": 4, "sundag": 6}
_MONTHS = {1: "januar", 3: "mars", 5: "mai", 11: "november"}
_ORD = [("første", 1), ("andre", 2), ("tredje", 3), ("fjerde", 4)]
_YEARS = (2019, 2020, 2021)


def _nth_weekday(y, m, wd, n):
    first = date(y, m, 1)
    offset = (wd - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


def _last_weekday(y, m, wd):
    nxt = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    last = nxt - timedelta(days=1)
    back = (last.weekday() - wd) % 7
    return last - timedelta(days=back)


_NTH = []
for _ordw, _n in _ORD:
    for _wdname, _wd in _WD.items():
        for _m, _mname in _MONTHS.items():
            for _y in _YEARS:
                _NTH.append((f"{_ordw} {_wdname} i {_mname} {_y}",
                             _nth_weekday(_y, _m, _wd, _n)))

_LAST = []
for _wdname, _wd in _WD.items():
    for _m, _mname in _MONTHS.items():
        for _y in _YEARS:
            _LAST.append((f"siste {_wdname} i {_mname} {_y}",
                          _last_weekday(_y, _m, _wd)))


@pytest.mark.parametrize("text,exp", _NTH)
def test_nth_weekday_of_month(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,exp", _LAST)
def test_last_weekday_of_month(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


def test_bare_last_weekday_is_anchor_relative():
    exp = ANCHOR.date() - timedelta(days=(ANCHOR.weekday() - 4) % 7 or 7)
    assert start("siste fredag") == AstroDate(exp.year, exp.month, exp.day)
