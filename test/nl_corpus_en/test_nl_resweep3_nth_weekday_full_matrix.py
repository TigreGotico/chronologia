"""Third-pass resweep: FULL matrix of the ordinal-weekday-of-month
construction ("the Nth <weekday> of <month> <year>") across all 12 months,
all 7 weekdays, all 5 ordinals (first/second/third/fourth/last), and a
fresh spread of years (2041-2060) disjoint from both the original file's
anchor-year spot checks and the second-pass resweep's 1980-2040 window.

Gold is an independent calendar scan (``calendar.monthrange`` + weekday
index), never the parser's own output -- identical oracle shape to the
prior resweep, just widened to the full 12-month axis and a new epoch.
"""
import calendar
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
       "friday": 4, "saturday": 5, "sunday": 6}
_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

_YEARS = (2041, 2045, 2050, 2055, 2060)


def _nth_weekday(year, month, wd, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == wd]
    return days[n - 1] if n >= 1 else days[-1]


def _cases():
    out = []
    for year in _YEARS:
        for mname, m in _MONTHS.items():
            for wname, wd in _WD.items():
                for oname, n in _ORD.items():
                    out.append(
                        (f"the {oname} {wname} of {mname} {year}",
                         year, m, wd, n))
    return out


@pytest.mark.parametrize("text,year,month,wd,n", _cases())
def test_nth_weekday_of_month_full_matrix_2040s2050s(text, year, month, wd, n):
    day = _nth_weekday(year, month, wd, n)
    s = date(year, month, day)
    e = s + timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
