# -*- coding: utf-8 -*-
"""da: year-qualified Danish holidays, fixed and computus-movable.

Every movable gold date is derived from the Western (Gregorian) computus
implemented here -- the Anonymous Gregorian algorithm -- not from the parser.
Fixed holidays are civil calendar constants.

    langfredag (Good Fri)          Easter - 2
    påskedag (Easter Sun)          Easter
    påskemandag (Easter Mon)       Easter + 1
    kristi himmelfartsdag (Asc.)   Easter + 39
    pinsedag (Pentecost)           Easter + 49
    2./anden pinsedag (Whit Mon)   Easter + 50

Bare (year-less) holidays live in test_nl_holiday_ref; here every phrase
carries an explicit year, and the span is the single day.

grundlovsdag (5 Jun), skærtorsdag (Easter-3) and store bededag (Easter+26)
are not resolved -- the parser returns the whole year -- so they are pinned
xfail rather than given a wrong gold.
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
    "juleaften": (12, 24),
    "juledag": (12, 25),
}
_MOVABLE = {
    "langfredag": -2,
    "påskedag": 0,
    "påskemandag": 1,
    "kristi himmelfartsdag": 39,
    "pinsedag": 49,
    "2. pinsedag": 50,
    "anden pinsedag": 50,
}
_YEARS = tuple(range(2018, 2028))

_CASES = []
for _y in _YEARS:
    for _name, (_mo, _da) in _FIXED.items():
        _CASES.append((f"{_name} {_y}", date(_y, _mo, _da)))
    _e = _easter(_y)
    for _name, _off in _MOVABLE.items():
        _CASES.append((f"{_name} {_y}", _e + timedelta(days=_off)))


@pytest.mark.parametrize("text,exp", _CASES)
def test_holiday_year(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
    assert span(text).width == timedelta(days=1)


@pytest.mark.xfail(strict=True, reason="holiday not resolved: parser returns "
                   "the whole year instead of the day")
@pytest.mark.parametrize("text,exp", [
    ("grundlovsdag 2020", date(2020, 6, 5)),
    ("grundlovsdag 2021", date(2021, 6, 5)),
    ("skærtorsdag 2020", _easter(2020) - timedelta(days=3)),
    ("skærtorsdag 2021", _easter(2021) - timedelta(days=3)),
    ("store bededag 2020", _easter(2020) + timedelta(days=26)),
    ("store bededag 2021", _easter(2021) + timedelta(days=26)),
])
def test_unresolved_holiday_xfail(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)
