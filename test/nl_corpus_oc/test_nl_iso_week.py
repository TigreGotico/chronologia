"""ISO-8601 weeks (oc), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('setmana 32', 2017, 32), ('setmana 1', 2017, 1), ('setmana 26', 2017, 26), ('setmana 52', 2017, 52), ('setmana 32 de 2026', 2026, 32), ('setmana 1 de 2026', 2026, 1), ('setmana 53 de 2020', 2020, 53), ('setmana 10 de 1999', 1999, 10), ('setmana 40 de 2024', 2024, 40), ('setmana 7 de 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['setmana 0', 'setmana 60', 'setmana 99 de 2020', 'setmana 53'])
def test_not_an_iso_week(text):
    nomatch(text)
