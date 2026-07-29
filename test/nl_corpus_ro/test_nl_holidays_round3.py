# -*- coding: utf-8 -*-
"""Round-3 NL holidays for Romanian: Crăciun (Christmas, Dec 25), its second
day (boxing_day, Dec 26), Ziua Muncii (May 1), plus the Orthodox movable
Paște (Orthodox Pascha) and Vinerea Mare (Orthodox Good Friday, Pascha-2).
Fixed gold is calendar arithmetic; Orthodox gold is an independent Meeus
Julian-computus date shifted 13 days onto the Gregorian civil calendar.
Anchor 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start

def _orthodox_easter(y):
    """Orthodox Pascha on the Gregorian civil calendar (Meeus Julian rule +
    the 13-day Julian->Gregorian shift valid 1900-2099)."""
    a = y % 4
    b = y % 7
    c = y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    mo = (d + e + 114) // 31
    da = ((d + e + 114) % 31) + 1
    return date(y, mo, da) + timedelta(days=13)


_YEARS = (2003, 2017, 2020, 2024, 2030, 2036, 2050, 2077, 2088, 2099)
_FIXED = [
    ("crăciun", 12, 25),
    ("a doua zi de crăciun", 12, 26),
    ("ziua muncii", 5, 1),
]
_FIXED_CASES = [(f"{name} {y}", y, m, d)
                for name, m, d in _FIXED for y in _YEARS]


@pytest.mark.parametrize("text,y,m,d", _FIXED_CASES, ids=[c[0] for c in _FIXED_CASES])
def test_round3_fixed_holiday(text, y, m, d):
    assert start(text) == AstroDate(y, m, d), text
    assert span(text).width == timedelta(days=1)


_MOV_CASES = []
for _y in _YEARS:
    _p = _orthodox_easter(_y)
    _MOV_CASES.append((f"paște {_y}".format(_y=_y), _p))
    _MOV_CASES.append((f"vinerea mare {_y}".format(_y=_y), _p - timedelta(days=2)))


@pytest.mark.parametrize("text,exp", _MOV_CASES, ids=[c[0] for c in _MOV_CASES])
def test_round3_orthodox_movable(text, exp):
    assert start(text) == AstroDate(exp.year, exp.month, exp.day), text
    assert span(text).width == timedelta(days=1)
