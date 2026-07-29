# -*- coding: utf-8 -*-
"""Hungarian Nth-weekday-of-month (``scoped_ordinal``).

Hungarian word order is MONTH(nominative) ORDINAL WEEKDAY+possessive:
"március harmadik hétfője" = the third Monday of March.  The ordinal
(harmadik) must bind as the ORDINAL and the possessive weekday (hétfője)
must be recognised, so the whole construction resolves to the exact date --
NOT read the ordinal as a day-of-month and strand the weekday.

Regression guard: a bare "MONTH ORDINAL" with no weekday still means the
day-of-month ("március harmadik" = March 3rd), unchanged.
"""
import calendar
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ad, span, start


def _nth_weekday(year, month, wd, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == wd]
    return days[n - 1] if n >= 1 else days[-1]


# weekday name (possessive) -> python weekday index
_WD = {
    "hétfője": 0, "keddje": 1, "szerdája": 2, "csütörtökje": 3,
    "péntekje": 4, "szombatja": 5, "vasárnapja": 6,
}
# ordinal word -> N
_ORD = {"első": 1, "második": 2, "harmadik": 3, "negyedik": 4}
_MONTHS = {"március": 3, "június": 6, "szeptember": 9, "november": 11}


def _cases():
    out = []
    for mname, m in _MONTHS.items():
        for wname, wd in _WD.items():
            for oname, n in _ORD.items():
                out.append((f"{mname} {oname} {wname}", m, wd, n))
    return out


@pytest.mark.parametrize("text,month,wd,n", _cases())
def test_nth_weekday_of_month(text, month, wd, n):
    day = _nth_weekday(2017, month, wd, n)
    assert start(text) == ad(datetime(2017, month, day))


def test_third_monday_of_march():
    # the canonical native-reviewer repro
    assert start("március harmadik hétfője") == ad(datetime(2017, 3, 20))


@pytest.mark.parametrize("text,year,month,wname,oname", [
    ("2020. március harmadik hétfője", 2020, 3, "hétfője", "harmadik"),
    ("2019. november első péntekje", 2019, 11, "péntekje", "első"),
])
def test_nth_weekday_of_month_year(text, year, month, wname, oname):
    day = _nth_weekday(year, month, _WD[wname], _ORD[oname])
    assert start(text) == ad(datetime(year, month, day))


# regression: bare "MONTH ORDINAL" (no weekday) stays the day-of-month reading
def test_bare_month_ordinal_is_day_of_month():
    s = span("március harmadik")
    assert (s.start.month, s.start.day) == (3, 3)
