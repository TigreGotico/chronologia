"""ISO-8601 weeks (it), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('settimana 32', 2017, 32), ('settimana 1', 2017, 1), ('settimana 26', 2017, 26), ('settimana 52', 2017, 52), ('settimana 32 del 2026', 2026, 32), ('settimana 1 del 2026', 2026, 1), ('settimana 53 del 2020', 2020, 53), ('settimana 10 del 1999', 1999, 10), ('settimana 40 del 2024', 2024, 40), ('settimana 7 del 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['settimana 0', 'settimana 60', 'settimana 99 del 2020', 'settimana 53'])
def test_not_an_iso_week(text):
    nomatch(text)
