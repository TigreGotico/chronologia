# -*- coding: utf-8 -*-
"""ISO-8601 weeks (fa), Monday-based by the standard, independent of the
Persian civil ``week_start`` (Saturday).  Mondays via date.fromisocalendar.
Head-first Persian order: ``هفته 32`` ("week 32"); ``در`` links the year."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [
    ('هفته 32', 2017, 32),
    ('هفته 1', 2017, 1),
    ('هفته 26', 2017, 26),
    ('هفته 52', 2017, 52),
    ('هفته 32 در 2026', 2026, 32),
    ('هفته 1 در 2026', 2026, 1),
    ('هفته 53 در 2020', 2020, 53),
    ('هفته 10 در 1999', 1999, 10),
]


@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("text", ['هفته 0', 'هفته 60', 'هفته 99 در 2020'])
def test_not_an_iso_week(text):
    nomatch(text)
