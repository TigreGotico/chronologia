# -*- coding: utf-8 -*-
"""Month-thirds (principis / mitjans / finals) sweep for Catalan.

Each third is an exact 1/3 slice of the calendar month: the boundaries fall at
day-1 + k * (days_in_month / 3) days, and since 86400 is divisible by 3 the
edge always lands on a whole number of seconds.  Expected bounds are computed
here from the real length of each month (leap February exercised via 2020),
never from the parser.  Resolution is inside the anchor year.
"""
from calendar import monthrange
from datetime import datetime, timedelta

import pytest

from ._corpus import parse, span, AstroDate

_THIRDS = [("principis", 0), ("mitjans", 1), ("finals", 2)]

_MONTHS = [
    ("gener", 1), ("febrer", 2), ("març", 3), ("abril", 4),
    ("maig", 5), ("juny", 6), ("juliol", 7), ("agost", 8),
    ("setembre", 9), ("octubre", 10), ("novembre", 11), ("desembre", 12),
]

_YEARS = (2017, 2020)  # 2020 exercises leap February


def _edge(year, month, k):
    dim = monthrange(year, month)[1]
    return datetime(year, month, 1) + timedelta(seconds=dim * 28800 * k)


def _prep(name):
    return "d'" if name[0] in "aeiou" else "de "


def _cases():
    out = []
    for y in _YEARS:
        for mo_name, mo in _MONTHS:
            text_tail = "%s%s" % (_prep(mo_name), mo_name)
            for word, k in _THIRDS:
                text = "%s %s" % (word, text_tail)
                s = _edge(y, mo, k)
                e = _edge(y, mo, k + 1)
                out.append((text, y, s, e))
    return out


_CASES = _cases()


@pytest.mark.parametrize(
    "text,year,s,e", _CASES, ids=["%s@%d" % (t, y) for t, y, _, _ in _CASES]
)
def test_month_third(text, year, s, e):
    anchor = datetime(year, 1, 1, 9, 0)
    sp = span(text, anchor)
    assert sp.start == AstroDate(s.year, s.month, s.day, s.hour, s.minute)
    assert sp.end == AstroDate(e.year, e.month, e.day, e.hour, e.minute)
    assert parse(text, anchor)[1] == ""
