# -*- coding: utf-8 -*-
"""ISO-8601 weeks (mwl), Monday-based by the standard.  Mondays via stdlib
date.fromisocalendar.  Mirandese head-first order: ``sumana 32``; ``de``
links the year."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('sumana 32', 2017, 32),
    ('sumana 1', 2017, 1),
    ('sumana 26', 2017, 26),
    ('sumana 52', 2017, 52),
    ('sumana 32 de 2026', 2026, 32),
    ('sumana 1 de 2026', 2026, 1),
    ('sumana 53 de 2020', 2020, 53),
    ('sumana 10 de 1999', 1999, 10),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['sumana 0', 'sumana 60', 'sumana 99 de 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
