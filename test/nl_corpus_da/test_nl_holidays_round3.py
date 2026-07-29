# -*- coding: utf-8 -*-
"""Round-3 NL holidays for Danish: the two movable feasts wired in round 3 --
Skærtorsdag (Maundy Thursday, Easter-3) and Store Bededag (Great Prayer Day,
the 4th Friday after Easter = Easter+26). Gold is the Western (Anonymous
Gregorian) computus, independent of the parser. Anchor 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start

def _easter(y):
    a = y % 19
    b, c = divmod(y, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31
    da = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, mo, da)


_YEARS = tuple(range(2015, 2035))
_CASES = []
for _y in _YEARS:
    _e = _easter(_y)
    _CASES.append((f"skærtorsdag {_y}".format(_y=_y), _e - timedelta(days=3)))
    _CASES.append((f"store bededag {_y}".format(_y=_y), _e + timedelta(days=26)))


@pytest.mark.parametrize("text,exp", _CASES, ids=[c[0] for c in _CASES])
def test_round3_movable_holiday(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day), text
    assert span(text).width == timedelta(days=1)
