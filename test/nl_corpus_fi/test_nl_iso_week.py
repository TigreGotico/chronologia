"""ISO-8601 weeks (fi), Monday-based by the standard. Mondays computed with
stdlib date.fromisocalendar; anchor 2017-06-27."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [('viikko 32', 2017, 32), ('viikko 1', 2017, 1), ('viikko 26', 2017, 26),
          ('viikko 52', 2017, 52), ('viikko 32 2026', 2026, 32), ('viikko 1 2026', 2026, 1),
          ('viikko 53 2020', 2020, 53), ('viikko 10 1999', 1999, 10),
          ('viikko 40 2024', 2024, 40), ('viikko 7 2030', 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ['viikko 0', 'viikko 60', 'viikko 99 2020', 'viikko 53'])
def test_not_an_iso_week(text):
    nomatch(text, A)
