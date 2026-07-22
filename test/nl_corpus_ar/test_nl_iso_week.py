# -*- coding: utf-8 -*-
"""ISO-8601 weeks (ar), Monday-based by the standard, independent of the
Arabic civil ``week_start`` (Saturday).  Mondays computed with stdlib
date.fromisocalendar.  Head-first Arabic order: ``الأسبوع 32`` ("week 32")."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('الأسبوع 32', 2017, 32),
    ('الأسبوع 1', 2017, 1),
    ('الأسبوع 26', 2017, 26),
    ('الأسبوع 52', 2017, 52),
    ('الأسبوع 32 من 2026', 2026, 32),
    ('الأسبوع 1 من 2026', 2026, 1),
    ('الأسبوع 53 من 2020', 2020, 53),
    ('الأسبوع 10 من 1999', 1999, 10),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['الأسبوع 0', 'الأسبوع 60', 'الأسبوع 99 من 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
