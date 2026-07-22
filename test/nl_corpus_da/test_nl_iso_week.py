"""ISO-8601 weeks (da), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('uge 32', 2017, 32), ('uge 1', 2017, 1), ('uge 26', 2017, 26), ('uge 52', 2017, 52), ('uge 32 af 2026', 2026, 32), ('uge 1 af 2026', 2026, 1), ('uge 53 af 2020', 2020, 53), ('uge 10 af 1999', 1999, 10), ('uge 40 af 2024', 2024, 40), ('uge 7 af 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['uge 0', 'uge 60', 'uge 99 af 2020', 'uge 53'])
def test_not_an_iso_week(text):
    nomatch(text)
