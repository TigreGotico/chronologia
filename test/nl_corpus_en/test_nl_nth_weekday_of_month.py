"""The ordinal-weekday-of-month construction: "the first Monday of July",
"the last Friday of November", "the second Saturday of June 2020".

A bare month keeps the anchor year (2017) -- this construction does NOT roll
to the future, so "the last Monday of May" stays in the already-past May 2017.
An explicit trailing year overrides that.  "last" selects the final matching
weekday of the month.  Every expected day is found by an independent calendar
scan, never by the parser.
"""
import calendar
from datetime import date

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end


_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
       "friday": 4, "saturday": 5, "sunday": 6}
_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}
_MONTHS = {"march": 3, "july": 7, "september": 9, "november": 11}


def _nth_weekday(year, month, wd, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == wd]
    return days[n - 1] if n >= 1 else days[-1]


def _cases():
    out = []
    for mname, m in _MONTHS.items():
        for wname, wd in _WD.items():
            for oname, n in _ORD.items():
                out.append((f"the {oname} {wname} of {mname}", m, wd, n))
    return out


@pytest.mark.parametrize("text,month,wd,n", _cases())
def test_nth_weekday_of_month(text, month, wd, n):
    day = _nth_weekday(2017, month, wd, n)
    s = date(2017, month, day)
    e = s + __import__("datetime").timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))


# explicit trailing year overrides the anchor-year default
@pytest.mark.parametrize("text,year,month,wname,oname", [
    ("the second saturday of june 2020", 2020, 6, "saturday", "second"),
    ("the first friday of april 2019", 2019, 4, "friday", "first"),
    ("the last thursday of november 2021", 2021, 11, "thursday", "last"),
    ("the third monday of january 2018", 2018, 1, "monday", "third"),
])
def test_nth_weekday_of_month_year(text, year, month, wname, oname):
    day = _nth_weekday(year, month, _WD[wname], _ORD[oname])
    s = date(year, month, day)
    e = s + __import__("datetime").timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
