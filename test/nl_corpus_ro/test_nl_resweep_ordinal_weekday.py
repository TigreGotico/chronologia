# -*- coding: utf-8 -*-
"""Second-pass Romanian ordinal-weekday-of-month sweep, fresh years.

Same construction as ``test_nl_ordinal_weekday.py`` -- ``<ordinal> <weekday>
din <month> <year>`` -- but over years that file does not touch (2015, 2016,
2025, 2027, 2028 here vs. 2017/2020-2024 there), so no (text, gold) pair is
duplicated. Gold is independent ``datetime.date`` arithmetic: walk to the
first matching weekday of the month and step in whole weeks.

Weekdays map to ``date.weekday()`` (Mon=0): luni=0, marți=1, miercuri=2,
joi=3, vineri=4, sâmbătă=5, duminică=6.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta
import calendar

import pytest

from ._corpus import start_end, nomatch, AstroDate

_WD = {
    "luni": 0, "marți": 1, "miercuri": 2, "joi": 3,
    "vineri": 4, "sâmbătă": 5, "duminică": 6,
}

_MONTH = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie", 5: "mai",
    6: "iunie", 7: "iulie", 8: "august", 9: "septembrie", 10: "octombrie",
    11: "noiembrie", 12: "decembrie",
}

_FRESH_YEARS = (2015, 2016, 2025, 2027, 2028)


def _nth_weekday(y, m, wd, n):
    first_wd = date(y, m, 1).weekday()
    day = 1 + (wd - first_wd) % 7 + (n - 1) * 7
    return day if day <= calendar.monthrange(y, m)[1] else None


def _last_weekday(y, m, wd):
    last = calendar.monthrange(y, m)[1]
    last_wd = date(y, m, last).weekday()
    return last - (last_wd - wd) % 7


# ---------------------------------------------------------------------------
# main sweep: 1st, 2nd, and last occurrence, fresh years x all months/weekdays
# ---------------------------------------------------------------------------
def _main_cases():
    out = []
    for y in _FRESH_YEARS:
        for m in range(1, 13):
            for wname, wd in _WD.items():
                out.append((f"primul {wname} din {_MONTH[m]} {y}",
                            _nth_weekday(y, m, wd, 1), y, m))
                out.append((f"a doua {wname} din {_MONTH[m]} {y}",
                            _nth_weekday(y, m, wd, 2), y, m))
                out.append((f"ultima {wname} din {_MONTH[m]} {y}",
                            _last_weekday(y, m, wd), y, m))
    return out


@pytest.mark.parametrize("text,day,y,m", _main_cases())
def test_ordinal_weekday_resweep(text, day, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, day), text
    assert e - s == timedelta(days=1)


# ---------------------------------------------------------------------------
# the fifth occurrence over two fresh years: present in some months, absent
# in others; absent -> the phrase must not resolve to a span.
# ---------------------------------------------------------------------------
def _fifth_cases():
    out = []
    for y in (2016, 2027):
        for m in range(1, 13):
            for wname, wd in _WD.items():
                day = _nth_weekday(y, m, wd, 5)
                out.append((f"a cincea {wname} din {_MONTH[m]} {y}", day, y, m))
    return out


@pytest.mark.parametrize("text,day,y,m", _fifth_cases())
def test_fifth_weekday_resweep(text, day, y, m):
    if day is None:
        nomatch(text)
    else:
        s, e = start_end(text)
        assert s == AstroDate(y, m, day), text
        assert e - s == timedelta(days=1)
