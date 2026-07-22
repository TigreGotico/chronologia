"""ISO-8601 weeks (nn), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('veke 32', 2017, 32), ('veke 1', 2017, 1), ('veke 26', 2017, 26), ('veke 52', 2017, 52), ('veke 32 av 2026', 2026, 32), ('veke 1 av 2026', 2026, 1), ('veke 53 av 2020', 2020, 53), ('veke 10 av 1999', 1999, 10), ('veke 40 av 2024', 2024, 40), ('veke 7 av 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['veke 0', 'veke 60', 'veke 99 av 2020', 'veke 53'])
def test_not_an_iso_week(text):
    nomatch(text)
