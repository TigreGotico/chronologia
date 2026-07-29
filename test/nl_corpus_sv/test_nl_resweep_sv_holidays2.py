# -*- coding: utf-8 -*-
"""sv (second-pass resweep): fixed + computus-movable holidays over fresh
years 2028-2047, disjoint from ``test_sv_holidays_year_sweep.py``'s
2018-2027 and from ``test_nl_national_holidays_2.py``'s 2018/2019 pins.

Also adds two names the first sweep never exercised at all: "sveriges
nationaldag" (fixed 6 June -- despite the stale "deferred" note in the first
sweep's docstring, it is in fact supported per
``test_nl_national_holidays_2.py``) and "annandag jul" (fixed 26 December,
Boxing Day / St Stephen's Day).

Every gold date is derived INDEPENDENTLY: fixed feasts from their statutory
calendar date, movable feasts from an anonymous-Gregorian computus that
offsets Easter Sunday. The parser is never consulted for the expected value.

Anchor 2017-06-27; every phrase carries an explicit year, so no roll applies.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start, parse, span

_YEARS = list(range(2028, 2048))


def _easter(year):
    """Anonymous Gregorian computus -> Easter Sunday (date)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


_FIXED = [
    ("nyårsdagen", lambda y: date(y, 1, 1)),
    ("trettondedag jul", lambda y: date(y, 1, 6)),
    ("första maj", lambda y: date(y, 5, 1)),
    ("sveriges nationaldag", lambda y: date(y, 6, 6)),
    ("julafton", lambda y: date(y, 12, 24)),
    ("juldagen", lambda y: date(y, 12, 25)),
    ("annandag jul", lambda y: date(y, 12, 26)),
]

_MOVABLE = [
    ("långfredagen", lambda y: _easter(y) - timedelta(days=2)),
    ("påskdagen", lambda y: _easter(y)),
    ("kristi himmelsfärds dag", lambda y: _easter(y) + timedelta(days=39)),
    ("pingstdagen", lambda y: _easter(y) + timedelta(days=49)),
]


def _cases(table):
    out = []
    for name, fn in table:
        for y in _YEARS:
            g = fn(y)
            out.append((f"{name} {y}", AstroDate(g.year, g.month, g.day)))
    return out


_FIXED_CASES = _cases(_FIXED)
_MOVABLE_CASES = _cases(_MOVABLE)


@pytest.mark.parametrize("text,gold", _FIXED_CASES,
                         ids=[c[0] for c in _FIXED_CASES])
def test_fixed_holiday_year_resweep(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,gold", _MOVABLE_CASES,
                         ids=[c[0] for c in _MOVABLE_CASES])
def test_movable_holiday_year_resweep(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == ""
