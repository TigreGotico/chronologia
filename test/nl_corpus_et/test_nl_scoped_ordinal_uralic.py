# -*- coding: utf-8 -*-
"""Estonian Nth-weekday-of-month (``scoped_ordinal``).

Estonian word order is MONTH(genitive) ORDINAL WEEKDAY:
"märtsi kolmas esmaspäev" = the third Monday of March.  The genitive month
(märtsi) and the ordinal (kolmas) must bind, so the construction resolves to
the exact date -- NOT read the ordinal as a day-of-month and strand the
weekday.
"""
import calendar
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ad, span, start


def _nth_weekday(year, month, wd, n):
    days = [d for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() == wd]
    return days[n - 1] if n >= 1 else days[-1]


_WD = {
    "esmaspäev": 0, "teisipäev": 1, "kolmapäev": 2, "neljapäev": 3,
    "reede": 4, "laupäev": 5, "pühapäev": 6,
}
_ORD = {"esimene": 1, "teine": 2, "kolmas": 3, "neljas": 4}
# genitive month surfaces
_MONTHS = {"märtsi": 3, "juuni": 6, "septembri": 9, "novembri": 11}


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
    assert start("märtsi kolmas esmaspäev") == ad(datetime(2017, 3, 20))


@pytest.mark.parametrize("text,year,month,wname,oname", [
    ("märtsi kolmas esmaspäev 2020", 2020, 3, "esmaspäev", "kolmas"),
    ("novembri esimene reede 2019", 2019, 11, "reede", "esimene"),
])
def test_nth_weekday_of_month_year(text, year, month, wname, oname):
    day = _nth_weekday(year, month, _WD[wname], _ORD[oname])
    assert start(text) == ad(datetime(year, month, day))
