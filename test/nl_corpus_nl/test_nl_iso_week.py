"""ISO-8601 weeks (nl), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('week 32', 2017, 32), ('week 1', 2017, 1), ('week 26', 2017, 26), ('week 52', 2017, 52), ('week 32 van 2026', 2026, 32), ('week 1 van 2026', 2026, 1), ('week 53 van 2020', 2020, 53), ('week 10 van 1999', 1999, 10), ('week 40 van 2024', 2024, 40), ('week 7 van 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['week 0', 'week 60', 'week 99 van 2020', 'week 53'])
def test_not_an_iso_week(text):
    nomatch(text)
