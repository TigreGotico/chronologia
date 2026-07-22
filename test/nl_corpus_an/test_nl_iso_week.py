# -*- coding: utf-8 -*-
"""ISO-8601 weeks (an), Monday-based by the standard.  Mondays via stdlib
date.fromisocalendar.  Aragonese head-first order: ``semana 32``; ``de`` links
the year."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('semana 32', 2018, 32),
    ('semana 1', 2018, 1),
    ('semana 26', 2018, 26),
    ('semana 52', 2018, 52),
    ('semana 32 de 2026', 2026, 32),
    ('semana 1 de 2026', 2026, 1),
    ('semana 53 de 2020', 2020, 53),
    ('semana 10 de 1999', 1999, 10),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['semana 0', 'semana 60', 'semana 99 de 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
