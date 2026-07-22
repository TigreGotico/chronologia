"""ISO-8601 weeks (kab), Monday-based by the standard; anchor 2017-06-27.
Kabyle names the week with amalas / dduṛt."""
from datetime import date, datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch

A = datetime(2017, 6, 27, 13, 4)
_CASES = [("amalas 32", 2017, 32), ("amalas 1", 2017, 1), ("amalas 26", 2017, 26),
          ("amalas 52", 2017, 52), ("amalas 32 2026", 2026, 32), ("amalas 1 2026", 2026, 1),
          ("dduṛt 53 2020", 2020, 53), ("dduṛt 10 1999", 1999, 10),
          ("amalas 40 2024", 2024, 40), ("amalas 7 2030", 2030, 7)]

@pytest.mark.parametrize("text,iy,iw", _CASES)
def test_iso_week(text, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text, A)
    assert s == AstroDate(mon.year, mon.month, mon.day)
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day)

@pytest.mark.parametrize("text", ["amalas 0", "amalas 60", "amalas 99 2020", "amalas 53"])
def test_not_an_iso_week(text):
    nomatch(text, A)
