"""ISO-8601 weeks (fy), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('wike 32', 2017, 32), ('wike 1', 2017, 1), ('wike 26', 2017, 26), ('wike 52', 2017, 52), ('wike 32 fan 2026', 2026, 32), ('wike 1 fan 2026', 2026, 1), ('wike 53 fan 2020', 2020, 53), ('wike 10 fan 1999', 1999, 10), ('wike 40 fan 2024', 2024, 40), ('wike 7 fan 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['wike 0', 'wike 60', 'wike 99 fan 2020', 'wike 53'])
def test_not_an_iso_week(text):
    nomatch(text)
