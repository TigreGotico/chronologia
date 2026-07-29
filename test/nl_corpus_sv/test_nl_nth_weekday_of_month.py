# -*- coding: utf-8 -*-
"""sv: "<ordinal> <weekday-definite> i <month> <year>" -- the Nth weekday of a
month, and "sista <weekday-definite> i <month> <year>" -- the last weekday.

Swedish scopes the ordinal/last weekday against the named month with the native
connector "i", and the weekday takes its DEFINITE form ("första måndagen i
januari 2020", "sista fredagen i mars 2020").  The gold day is computed by
independent calendar arithmetic and is never read back from the parser.  n is
kept to 1..4 so the target weekday always exists in every month.

A BARE "förra <weekday>" with NO trailing month stays anchor-relative
(weekday_ref); only the month-scoped "sista ... i <month>" form nests into
scoped_ordinal.
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, AstroDate, ANCHOR

_WD = {"måndagen": 0, "onsdagen": 2, "fredagen": 4, "söndagen": 6}
_MONTHS = {1: "januari", 3: "mars", 5: "maj", 11: "november"}
_ORD = [("första", 1), ("andra", 2), ("tredje", 3), ("fjärde", 4)]
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
            _LAST.append((f"sista {_wdname} i {_mname} {_y}",
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
    # weekday_ref "last" in Swedish is "förra" (not "sista", which is the
    # month-scoping ordlast marker).  The last Friday before the Tuesday anchor
    # (2017-06-27) is 2017-06-23 -- a plain anchor-relative reading.
    exp = ANCHOR.date() - timedelta(days=(ANCHOR.weekday() - 4) % 7 or 7)
    assert start("förra fredagen") == AstroDate(exp.year, exp.month, exp.day)
