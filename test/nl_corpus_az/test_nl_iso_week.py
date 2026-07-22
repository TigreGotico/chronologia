"""ISO-8601 weeks (az), Monday-based by the standard; anchor 2017-06-27. The
unambiguous "həftə N" surface is asserted (the ordinal "32. həftə" collides with
the Nth-week scoped-ordinal reading)."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [("həftə 32", 2017, 32), ("həftə 1", 2017, 1), ("həftə 26", 2017, 26),
          ("həftə 52", 2017, 52), ("həftə 32 2026", 2026, 32), ("həftə 1 2026", 2026, 1),
          ("həftə 53 2020", 2020, 53), ("həftə 10 1999", 1999, 10),
          ("həftə 40 2024", 2024, 40), ("həftə 7 2030", 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ["həftə 0", "həftə 60", "həftə 99 2020", "həftə 53"])
def test_not_an_iso_week(text):
    nomatch(text, A)
