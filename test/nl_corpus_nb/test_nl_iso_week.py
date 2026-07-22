"""ISO-8601 weeks (nb), Monday-based by the standard, independent of the
locale civil week_start. Mondays computed with stdlib date.fromisocalendar."""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

_CASES = [('uke 32', 2017, 32), ('uke 1', 2017, 1), ('uke 26', 2017, 26), ('uke 52', 2017, 52), ('uke 32 av 2026', 2026, 32), ('uke 1 av 2026', 2026, 1), ('uke 53 av 2020', 2020, 53), ('uke 10 av 1999', 1999, 10), ('uke 40 av 2024', 2024, 40), ('uke 7 av 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['uke 0', 'uke 60', 'uke 99 av 2020', 'uke 53'])
def test_not_an_iso_week(text):
    nomatch(text)
