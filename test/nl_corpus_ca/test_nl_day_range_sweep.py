# -*- coding: utf-8 -*-
"""Closed day-range ("del X al Y de <month>") sweep for Catalan.

The range is inclusive on both ends, so the parsed span runs from day X 00:00
to day (Y+1) 00:00.  Anchoring on 1 January keeps every February..December
range in the anchor year, so the expected bounds are pure arithmetic here.
Expected values never touch the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import parse, start_end, AstroDate

_MONTHS = [
    ("febrer", 2), ("març", 3), ("abril", 4), ("maig", 5), ("juny", 6),
    ("juliol", 7), ("agost", 8), ("setembre", 9), ("octubre", 10),
    ("novembre", 11), ("desembre", 12),
]

# (X, Y) inclusive day pairs, X >= 2, Y <= 27 so day Y+1 always exists.
_PAIRS = [(2, 7), (3, 8), (5, 12), (10, 20), (20, 25), (6, 27)]

_YEARS = (2018, 2021)


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
def test_day_range(text, year, s, e):
    anchor = datetime(year, 1, 1, 9, 0)
    gs, ge = start_end(text, anchor)
    assert gs == AstroDate(s.year, s.month, s.day)
    assert ge == AstroDate(e.year, e.month, e.day)
    assert parse(text, anchor)[1] == ""
