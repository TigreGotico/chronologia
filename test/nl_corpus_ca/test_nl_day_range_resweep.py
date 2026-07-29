# -*- coding: utf-8 -*-
"""Second-pass closed day-range ("del X al Y de <month>") sweep for Catalan --
fresh years, disjoint from ``test_nl_day_range_sweep.py`` (2018, 2021) and
fresh (X, Y) pairs.  Same inclusive-range semantics: the parsed span runs
from day X 00:00 to day (Y+1) 00:00, so expected bounds are pure arithmetic,
never touching the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import parse, start_end, AstroDate

_MONTHS = [
    ("gener", 1), ("febrer", 2), ("març", 3), ("abril", 4), ("maig", 5),
    ("juny", 6), ("juliol", 7), ("agost", 8), ("setembre", 9),
    ("octubre", 10), ("novembre", 11), ("desembre", 12),
]

# fresh (X, Y) inclusive day pairs, X >= 2, Y <= 27.
_PAIRS = [(2, 9), (4, 11), (6, 14), (8, 19), (11, 23), (15, 26)]

_YEARS = (2019, 2023, 2027)


def _prep(name):
    return "d'" if name[0] in "aeiou" else "de "


def _cases():
    out = []
    for y in _YEARS:
        for mo_name, mo in _MONTHS:
            tail = "%s%s" % (_prep(mo_name), mo_name)
            for x, z in _PAIRS:
                text = "del %d al %d %s" % (x, z, tail)
                s = datetime(y, mo, x)
                e = datetime(y, mo, z) + timedelta(days=1)
                out.append((text, y, s, e))
    return out


_CASES = _cases()


@pytest.mark.parametrize(
    "text,year,s,e", _CASES, ids=["%s@%d" % (t, y) for t, y, _, _ in _CASES]
)
def test_day_range_fresh(text, year, s, e):
    anchor = datetime(year, 1, 1, 9, 0)
    gs, ge = start_end(text, anchor)
    assert gs == AstroDate(s.year, s.month, s.day)
    assert ge == AstroDate(e.year, e.month, e.day)
    assert parse(text, anchor)[1] == ""
