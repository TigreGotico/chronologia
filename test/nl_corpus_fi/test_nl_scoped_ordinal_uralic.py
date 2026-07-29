# -*- coding: utf-8 -*-
"""Finnish Nth-weekday-of-month (``scoped_ordinal``).

Finnish word order is MONTH(genitive) ORDINAL WEEKDAY:
"maaliskuun kolmas maanantai" = the third Monday of March.  The genitive
month (maaliskuun) and the ordinal (kolmas) must bind, so the construction
resolves to the exact date -- NOT read the ordinal as a day-of-month and
strand the weekday.
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
    "maanantai": 0, "tiistai": 1, "keskiviikko": 2, "torstai": 3,
    "perjantai": 4, "lauantai": 5, "sunnuntai": 6,
}
_ORD = {"ensimmäinen": 1, "toinen": 2, "kolmas": 3, "neljäs": 4}
# genitive month surfaces
_MONTHS = {"maaliskuun": 3, "kesäkuun": 6, "syyskuun": 9, "marraskuun": 11}


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
    assert start("maaliskuun kolmas maanantai") == ad(datetime(2017, 3, 20))


@pytest.mark.parametrize("text,year,month,wname,oname", [
    ("maaliskuun kolmas maanantai 2020", 2020, 3, "maanantai", "kolmas"),
    ("marraskuun ensimmäinen perjantai 2019", 2019, 11, "perjantai",
     "ensimmäinen"),
])
def test_nth_weekday_of_month_year(text, year, month, wname, oname):
    day = _nth_weekday(year, month, _WD[wname], _ORD[oname])
    assert start(text) == ad(datetime(year, month, day))
