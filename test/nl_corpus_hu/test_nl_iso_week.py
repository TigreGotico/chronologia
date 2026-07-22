"""ISO-8601 weeks (hu), Monday-based by the standard; anchor 2017-06-27.
The bare Hungarian ordinal form "32. hét" collides with the Nth-week
scoped-ordinal reading, so the unambiguous "hét N" surface is asserted here."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [("hét 32", 2017, 32), ("hét 1", 2017, 1), ("hét 26", 2017, 26),
          ("hét 52", 2017, 52), ("hét 32 2026", 2026, 32), ("hét 1 2026", 2026, 1),
          ("hét 53 2020", 2020, 53), ("hét 10 1999", 1999, 10),
          ("hét 40 2024", 2024, 40), ("hét 7 2030", 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ["hét 0", "hét 60", "hét 99 2020", "hét 53"])
def test_not_an_iso_week(text):
    nomatch(text, A)
