# -*- coding: utf-8 -*-
"""Gregorian-calendar dates written with Persian month names.

The fa locale also reads the Gregorian months (ژانویه ... دسامبر).  Gold here
is the plain Gregorian calendar, so it is trivially independent of the engine.
Full dates resolve to a one-day span; a bare month + year resolves to the
whole calendar month.
"""
from datetime import date, timedelta

import pytest

from ._corpus import ad, start, start_end, AstroDate

GMON = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
        "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]

_YEARS = [2018, 2019, 2020, 2021, 2022]
_DAYS = [1, 5, 10, 15, 20, 25, 28]


@pytest.mark.parametrize("text,y,m,d", [
    (f"{d} {GMON[m - 1]} {y}", y, m, d)
    for y in _YEARS for m in range(1, 13) for d in _DAYS
])
def test_gregorian_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m", [
    (f"{GMON[m - 1]} {y}", y, m) for y in _YEARS for m in range(1, 13)
])
def test_gregorian_month_year_span(text, y, m):
    from datetime import datetime
    s = date(y, m, 1)
    e = date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    assert start_end(text) == (ad(datetime(s.year, s.month, s.day)),
                               ad(datetime(e.year, e.month, e.day)))
