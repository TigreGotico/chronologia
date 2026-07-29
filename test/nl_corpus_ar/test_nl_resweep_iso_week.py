# -*- coding: utf-8 -*-
"""Second-pass oracle re-sweep: ISO-8601 weeks (ar), fresh week/year pairs
disjoint from ``test_nl_iso_week``.  Mondays computed with stdlib
date.fromisocalendar; independent of the parser.  Head-first Arabic order:
``الأسبوع N من YEAR``."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('الأسبوع 5 من 2003', 2003, 5),
    ('الأسبوع 40 من 2011', 2011, 40),
    ('الأسبوع 22 من 2018', 2018, 22),
    ('الأسبوع 48 من 2022', 2022, 48),
    ('الأسبوع 15 من 2031', 2031, 15),
    ('الأسبوع 33 من 1994', 1994, 33),
    ('الأسبوع 2 من 2040', 2040, 2),
    ('الأسبوع 51 من 1988', 1988, 51),
    ('الأسبوع 27 من 2016', 2016, 27),
    ('الأسبوع 44 من 2029', 2029, 44),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week_resweep(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['الأسبوع 0', 'الأسبوع 61', 'الأسبوع 88 من 2019'])
def test_not_an_iso_week_resweep(text):
    nomatch(text)
