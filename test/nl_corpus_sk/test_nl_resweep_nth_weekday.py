# -*- coding: utf-8 -*-
"""Second-pass sweep: "Nth <weekday> v <month-locative> <year>" (sk), fresh years.

Extends test_sk_scoped_weekday_bugs_xfail.py (a handful of spot-checks, now
passing after PR #354 fixed locative-month and scoped-ordinal reading) with a
dense grid: all 7 weekdays x ordinals 1st-4th x all 12 months x fresh years
2016/2022/2027, plus the "posledný/posledná" (last) form over the same grid.
The ordinal agrees in gender with the weekday noun (masc. pondelok/utorok/
štvrtok/piatok -> prvý/druhý/tretí/štvrtý/posledný; fem. streda/sobota/nedeľa
-> prvá/druhá/tretia/štvrtá/posledná). February takes the euphonic "vo"
preposition ("vo februári"), every other month takes "v". Gold is the Nth (or
last) matching weekday of the month, computed by independent ``date``
arithmetic -- the parser is never consulted for the expected value. Anchor
Tue 2017-06-27 13:04."""
from calendar import monthrange
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

_WD = {
    "pondelok": (0, "m"), "utorok": (1, "m"), "streda": (2, "f"),
    "štvrtok": (3, "m"), "piatok": (4, "m"), "sobota": (5, "f"),
    "nedeľa": (6, "f"),
}
_ORD = {1: {"m": "prvý", "f": "prvá"}, 2: {"m": "druhý", "f": "druhá"},
         3: {"m": "tretí", "f": "tretia"}, 4: {"m": "štvrtý", "f": "štvrtá"}}
_POSL = {"m": "posledný", "f": "posledná"}
_LOC = [None, "januári", "februári", "marci", "apríli", "máji", "júni",
        "júli", "auguste", "septembri", "októbri", "novembri", "decembri"]

_YEARS = (2016, 2022, 2027)


def _prep(m):
    return "vo" if m == 2 else "v"


def _nth_weekday(y, m, wd, n):
    d = date(y, m, 1)
    off = (wd - d.weekday()) % 7
    dd = date(y, m, 1 + off + 7 * (n - 1))
    assert dd.month == m
    return dd


def _last_weekday(y, m, wd):
    last = monthrange(y, m)[1]
    d = date(y, m, last)
    return d - timedelta(days=(d.weekday() - wd) % 7)


def _day(d):
    nxt = d + timedelta(days=1)
    return AstroDate(d.year, d.month, d.day), AstroDate(nxt.year, nxt.month, nxt.day)


_NTH_CASES = []
for _wd_name, (_wd_idx, _gender) in _WD.items():
    for _n in (1, 2, 3, 4):
        _ordw = _ORD[_n][_gender]
        for _m in range(1, 13):
            for _y in _YEARS:
                _NTH_CASES.append(
                    (f"{_ordw} {_wd_name} {_prep(_m)} {_LOC[_m]} {_y}",
                     _nth_weekday(_y, _m, _wd_idx, _n)))

_LAST_CASES = []
for _wd_name, (_wd_idx, _gender) in _WD.items():
    _ordw = _POSL[_gender]
    for _m in range(1, 13):
        for _y in _YEARS:
            _LAST_CASES.append(
                (f"{_ordw} {_wd_name} {_prep(_m)} {_LOC[_m]} {_y}",
                 _last_weekday(_y, _m, _wd_idx)))


@pytest.mark.parametrize("text,gold", _NTH_CASES)
def test_nth_weekday_of_month_fresh(text, gold):
    assert start_end(text) == _day(gold), text


@pytest.mark.parametrize("text,gold", _LAST_CASES)
def test_last_weekday_of_month_fresh(text, gold):
    assert start_end(text) == _day(gold), text
