# -*- coding: utf-8 -*-
"""ISO-8601 weeks (uk), Monday-based by the standard, independent of the civil
week_start. Mondays computed with stdlib date.fromisocalendar -- never the
parser."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('тиждень 32', 2017, 32),
    ('тиждень 1', 2017, 1),
    ('тиждень 26', 2017, 26),
    ('тиждень 52', 2017, 52),
    ('тиждень 32 2026', 2026, 32),
    ('тиждень 10 1999', 1999, 10),
    ('тиждень 40 2024', 2024, 40),
    ('тиждень 7 2030', 2030, 7),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['тиждень 0', 'тиждень 60', 'тиждень 99 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
