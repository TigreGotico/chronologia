"""ISO-8601 weeks (tr), Monday-based by the standard; anchor 2017-06-27. The
bare Turkish ordinal "32. hafta" collides with the Nth-week scoped-ordinal
reading, so the unambiguous "hafta N" surface is asserted here."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [("hafta 32", 2017, 32), ("hafta 1", 2017, 1), ("hafta 26", 2017, 26),
          ("hafta 52", 2017, 52), ("hafta 32 2026", 2026, 32), ("hafta 1 2026", 2026, 1),
          ("hafta 53 2020", 2020, 53), ("hafta 10 1999", 1999, 10),
          ("hafta 40 2024", 2024, 40), ("hafta 7 2030", 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ["hafta 0", "hafta 60", "hafta 99 2020", "hafta 53"])
def test_not_an_iso_week(text):
    nomatch(text, A)
