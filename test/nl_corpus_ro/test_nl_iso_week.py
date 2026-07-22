"""ISO-8601 weeks (ro), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('săptămâna 32', 2017, 32), ('săptămâna 1', 2017, 1), ('săptămâna 26', 2017, 26), ('săptămâna 52', 2017, 52), ('săptămâna 32 din 2026', 2026, 32), ('săptămâna 1 din 2026', 2026, 1), ('săptămâna 53 din 2020', 2020, 53), ('săptămâna 10 din 1999', 1999, 10), ('săptămâna 40 din 2024', 2024, 40), ('săptămâna 7 din 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['săptămâna 0', 'săptămâna 60', 'săptămâna 99 din 2020', 'săptămâna 53'])
def test_not_an_iso_week(text):
    nomatch(text)
