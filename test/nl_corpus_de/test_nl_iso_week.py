"""ISO-8601 weeks (de), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('woche 32', 2017, 32), ('kw 32', 2017, 32), ('woche 1', 2017, 1), ('woche 52', 2017, 52), ('woche 32 von 2026', 2026, 32), ('woche 1 von 2026', 2026, 1), ('woche 53 von 2020', 2020, 53), ('woche 10 von 1999', 1999, 10), ('woche 40 von 2024', 2024, 40), ('kw 7 von 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['woche 0', 'woche 60', 'woche 99 von 2020', 'woche 53'])
def test_not_an_iso_week(text):
    nomatch(text)
