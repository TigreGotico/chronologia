"""Second-pass resweep: FULL matrix of the ordinal-weekday-of-month
construction ("the Nth <weekday> of <month> <year>") across all 12 months,
all 7 weekdays, all 5 ordinals (first/second/third/fourth/last), and a
spread of explicit years.

``test_nl_nth_weekday_of_month.py`` only covers 4 months (march, july,
september, november) with the anchor year, plus 4 explicit-year spot checks.
This file fills in the remaining 8 months and cross-products them with
explicit years so the construction is exercised over a much wider calendar
and epoch range.  Gold is an independent calendar scan
(``calendar.monthrange`` + weekday index), never the parser's own output --
identical oracle shape to the original file, just widened.
"""
import calendar
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
       "friday": 4, "saturday": 5, "sunday": 6}
_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "last": -1}

# the 8 months NOT covered by the original file's bare (no-year) matrix
_NEW_MONTHS = {
    "january": 1, "february": 2, "april": 4, "may": 5,
    "june": 6, "august": 8, "october": 10, "december": 12,
}

_YEARS = (2010, 2015, 2020, 2024)


def _nth_weekday(year, month, wd, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == wd]
    return days[n - 1] if n >= 1 else days[-1]


def _cases():
    out = []
    for year in _YEARS:
        for mname, m in _NEW_MONTHS.items():
            for wname, wd in _WD.items():
                for oname, n in _ORD.items():
                    out.append(
                        (f"the {oname} {wname} of {mname} {year}",
                         year, m, wd, n))
    return out


@pytest.mark.parametrize("text,year,month,wd,n", _cases())
def test_nth_weekday_of_month_year_matrix(text, year, month, wd, n):
    day = _nth_weekday(year, month, wd, n)
    s = date(year, month, day)
    e = s + timedelta(days=1)
    assert start_end(text) == (AstroDate(s.year, s.month, s.day),
                               AstroDate(e.year, e.month, e.day))
