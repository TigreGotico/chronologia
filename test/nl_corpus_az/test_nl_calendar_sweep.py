# -*- coding: utf-8 -*-
"""Broad Gregorian date sweep in Azerbaijani (DMY order, "5 mart 2019").

Gold is pure calendar arithmetic.  A bare day+month with no year resolves to
the next such date at or after the anchor date (2017-06-27): same year if the
date has not yet passed, otherwise the following year.
"""
from datetime import date, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start, start_end, span, ANCHOR

_AD = ANCHOR.date()

MONTHS = {
    1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel", 5: "may", 6: "iyun",
    7: "iyul", 8: "avqust", 9: "sentyabr", 10: "oktyabr", 11: "noyabr",
    12: "dekabr",
}


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


# ---- day + month, no year: sweep day 10 and day 22 across all 12 months ----
_NOYEAR = [(m, d) for m in range(1, 13) for d in (10, 22)]


@pytest.mark.parametrize("m,d", _NOYEAR)
def test_day_month_no_year(m, d):
    y = _fy(m, d)
    txt = "%d %s" % (d, MONTHS[m])
    assert start(txt) == AstroDate(y, m, d)
    assert span(txt).width == timedelta(days=1)


# ---- day + month + year: day 15 across all months, several years ----
_WITHYEAR = [(y, m, d)
             for y in (1912, 1945, 1969, 1991, 2008, 2019, 2023, 2031)
             for m in range(1, 13) for d in (7, 15, 23)]


@pytest.mark.parametrize("y,m,d", _WITHYEAR)
def test_day_month_year(y, m, d):
    txt = "%d %s %d" % (d, MONTHS[m], y)
    assert start(txt) == AstroDate(y, m, d)
    assert span(txt).width == timedelta(days=1)


# ---- month-end edges: last valid day of each month in a non-leap year ----
_LASTDAY = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
            9: 30, 10: 31, 11: 30, 12: 31}


@pytest.mark.parametrize("m,d", sorted(_LASTDAY.items()))
def test_month_last_day_2019(m, d):
    txt = "%d %s 2019" % (d, MONTHS[m])
    assert start(txt) == AstroDate(2019, m, d)


# ---- bare month + year across all 12 months ----
@pytest.mark.parametrize("y", [1999, 2020, 2026, 2033])
@pytest.mark.parametrize("m", range(1, 13))
def test_month_year(m, y):
    s, e = start_end("%s %d" % (MONTHS[m], y))
    assert s == AstroDate(y, m, 1)
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    assert e == AstroDate(ny, nm, 1)
