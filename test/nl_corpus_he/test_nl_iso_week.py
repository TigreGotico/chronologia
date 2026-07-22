# -*- coding: utf-8 -*-
"""ISO-8601 weeks (he), Monday-based by the standard, independent of the
Hebrew civil ``week_start`` (Sunday).  Mondays via stdlib date.fromisocalendar.
Head-first Hebrew order: ``שבוע 32`` ("week 32")."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('שבוע 32', 2017, 32),
    ('שבוע 1', 2017, 1),
    ('שבוע 26', 2017, 26),
    ('שבוע 52', 2017, 52),
    ('שבוע 32 של 2026', 2026, 32),
    ('שבוע 1 של 2026', 2026, 1),
    ('שבוע 53 של 2020', 2020, 53),
    ('שבוע 10 של 1999', 1999, 10),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['שבוע 0', 'שבוע 60', 'שבוע 99 של 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
