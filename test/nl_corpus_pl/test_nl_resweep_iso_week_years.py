# -*- coding: utf-8 -*-
"""SECOND-PASS resweep: ISO-8601 weeks (pl), swept across many fresh
week-numbers and years to extend the small hand-picked list in
``test_nl_iso_week.py`` (which only touches weeks 1/32/52/26/10/40/7 against
years 2026/1999/2024/2030 explicitly, plus bare weeks against the anchor
year). Monday-based per the ISO standard, computed with stdlib
``date.fromisocalendar`` -- never the parser.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import nomatch, start_end

#: fresh week numbers -- disjoint from the first-pass 1/32/52/26/10/40/7.
_WEEKS = (3, 8, 16, 22, 29, 35, 44, 48)
#: fresh years -- disjoint from the first-pass 2026/1999/2024/2030.
_YEARS = (2012, 2014, 2017, 2021, 2027, 2032)


def _cases():
    out = []
    for y in _YEARS:
        for w in _WEEKS:
            # ISO year `y` does not always have a week 53; every week here is
            # <=52 so it is always valid for any ISO year.
            out.append((f"tydzień {w} {y}", y, w))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,iy,iw", _CASES, ids=[c[0] for c in _CASES])
def test_iso_week_resweep(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ["tydzień 0 2025", "tydzień 60 2025"])
def test_not_an_iso_week_resweep(text):
    nomatch(text)
