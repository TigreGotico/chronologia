# -*- coding: utf-8 -*-
"""Relative offset sweeps in Turkish: N <unit> sonra / önce.

"sonra" = after (positive), "önce" = before (negative).  Day/week/hour/minute
offsets are plain timedelta from the anchor; month/year offsets are calendar
(relativedelta).  The oracle computes each target independently.
Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import start

A = datetime(2017, 6, 27, 13, 4)


def _check(text, target):
    s = start(text, A)
    assert (s.year, s.month, s.day, s.hour, s.minute) == (
        target.year, target.month, target.day, target.hour, target.minute)


@pytest.mark.parametrize("n", [1, 2, 3, 5, 7, 10, 21, 45, 100, 365])
def test_day_offsets(n):
    _check(f"{n} gün sonra", A + timedelta(days=n))
    _check(f"{n} gün önce", A - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 6, 8, 12, 26, 52])
def test_week_offsets(n):
    _check(f"{n} hafta sonra", A + timedelta(weeks=n))
    _check(f"{n} hafta önce", A - timedelta(weeks=n))


@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 12, 18, 23])
def test_hour_offsets(n):
    _check(f"{n} saat sonra", A + timedelta(hours=n))
    _check(f"{n} saat önce", A - timedelta(hours=n))


@pytest.mark.parametrize("n", [5, 10, 15, 20, 30, 45, 90, 120])
def test_minute_offsets(n):
    _check(f"{n} dakika sonra", A + timedelta(minutes=n))
    _check(f"{n} dakika önce", A - timedelta(minutes=n))


@pytest.mark.parametrize("n", [1, 2, 3, 4, 6, 9, 12, 18, 24])
def test_month_offsets(n):
    _check(f"{n} ay sonra", A + relativedelta(months=n))
    _check(f"{n} ay önce", A - relativedelta(months=n))


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 20, 50, 100])
def test_year_offsets(n):
    _check(f"{n} yıl sonra", A + relativedelta(years=n))
    _check(f"{n} yıl önce", A - relativedelta(years=n))
