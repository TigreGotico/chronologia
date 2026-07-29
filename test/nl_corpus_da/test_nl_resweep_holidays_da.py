# -*- coding: utf-8 -*-
"""da (second-pass resweep): Danish holidays over 20 fresh years (2028-2047),
not exercised by ``test_da_holidays_computus.py`` (2018-2027) or
``test_nl_national_holidays_2.py`` (bare/2018-2019).

Fixed civil dates:
    nytårsdag        1 Jan
    grundlovsdag      5 Jun
    juleaftensdag    24 Dec
    1. juledag       25 Dec
    2. juledag       26 Dec

Movable, derived from the Anonymous Gregorian computus (independent of the
parser):
    skærtorsdag (Maundy Thu)     Easter - 3
    langfredag (Good Fri)        Easter - 2
    påske (Easter Sun)           Easter
    store bededag (Great Prayer) Easter + 26
    kristi himmelfartsdag (Asc.) Easter + 39
    pinse (Pentecost)            Easter + 49

skærtorsdag and store bededag are still unresolved by the parser -- it
strands them on the whole calendar year -- so those two remain pinned xfail
with the correct computus gold (never a wrong one).
"""
from datetime import date, timedelta

import pytest

from ._corpus import start, span, AstroDate


def _easter(y):
    a = y % 19
    b, c = divmod(y, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(y, month, day)


_FIXED = {
    "nytårsdag": (1, 1),
    "grundlovsdag": (6, 5),
    "juleaftensdag": (12, 24),
    "1. juledag": (12, 25),
    "2. juledag": (12, 26),
}
_MOVABLE_OK = {
    "langfredag": -2,
    "påske": 0,
    "kristi himmelfartsdag": 39,
    "pinse": 49,
}
_MOVABLE_XFAIL = {
    "skærtorsdag": -3,
    "store bededag": 26,
}
_YEARS = tuple(range(2028, 2048))

_FIXED_CASES = []
_MOVABLE_CASES = []
_XFAIL_CASES = []
for _y in _YEARS:
    for _name, (_mo, _da) in _FIXED.items():
        _FIXED_CASES.append((f"{_name} {_y}", date(_y, _mo, _da)))
    _e = _easter(_y)
    for _name, _off in _MOVABLE_OK.items():
        _MOVABLE_CASES.append((f"{_name} {_y}", _e + timedelta(days=_off)))
    for _name, _off in _MOVABLE_XFAIL.items():
        _XFAIL_CASES.append((f"{_name} {_y}", _e + timedelta(days=_off)))


@pytest.mark.parametrize("text,exp", _FIXED_CASES)
def test_fixed_holiday_year_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,exp", _MOVABLE_CASES)
def test_movable_holiday_year_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.xfail(strict=True, reason="holiday not resolved: parser returns "
                   "the whole year instead of the day")
@pytest.mark.parametrize("text,exp", _XFAIL_CASES)
def test_unresolved_holiday_xfail_fresh(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
