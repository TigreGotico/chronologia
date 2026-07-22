"""ISO-8601 weeks (et), Monday-based by the standard; anchor 2017-06-27.
Mondays via stdlib date.fromisocalendar."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [("nädal 32", 2017, 32), ("nädal 1", 2017, 1), ("nädal 26", 2017, 26),
          ("nädal 52", 2017, 52), ("nädal 32 2026", 2026, 32), ("nädal 1 2026", 2026, 1),
          ("nädal 53 2020", 2020, 53), ("nädal 10 1999", 1999, 10),
          ("nädal 40 2024", 2024, 40), ("nädal 7 2030", 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ["nädal 0", "nädal 60", "nädal 99 2020", "nädal 53"])
def test_not_an_iso_week(text):
    nomatch(text, A)
