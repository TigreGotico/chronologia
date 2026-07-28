"""Year-first Hungarian calendar dates swept across many years, months and
days ("2011. augusztus 20.").  The surface is YEAR. month-name DAY. with the
ordinal dot -- the Academy's written-date order (AkH. 297).  Each date binds a
single calendar day; the expected span is computed by independent ``datetime``
arithmetic (start day, next day), never from the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end

MONTHS = [
    "január", "február", "március", "április", "május", "június",
    "július", "augusztus", "szeptember", "október", "november", "december",
]


def _fmt(y, mo, d):
    return f"{y}. {MONTHS[mo - 1]} {d}."


def _day_span(y, mo, d):
    s = datetime(y, mo, d)
    return ad(s), ad(s + timedelta(days=1))


# -- the 15th of every month across a quarter-century --------------------
_MIDMONTH = [(y, mo) for y in range(2000, 2026) for mo in range(1, 13)]


@pytest.mark.parametrize("y,mo", _MIDMONTH)
def test_midmonth_sweep(y, mo):
    assert start_end(_fmt(y, mo, 15)) == _day_span(y, mo, 15)


# -- a day sweep within single years (first, tenth, twentieth, month end) --
def _valid(y, mo, d):
    try:
        datetime(y, mo, d)
        return True
    except ValueError:
        return False


_DAYSWEEP = [
    (y, mo, d)
    for y in (2019, 2020, 2021, 2024)
    for mo in range(1, 13)
    for d in (1, 10, 20, 28)
    if _valid(y, mo, d)
]


@pytest.mark.parametrize("y,mo,d", _DAYSWEEP)
def test_day_sweep(y, mo, d):
    assert start_end(_fmt(y, mo, d)) == _day_span(y, mo, d)


# -- true month-end days, including the leap-day boundary ----------------
_MONTH_ENDS = [
    (2020, 1, 31), (2020, 2, 29), (2019, 2, 28), (2020, 3, 31),
    (2020, 4, 30), (2020, 5, 31), (2020, 6, 30), (2020, 7, 31),
    (2020, 8, 31), (2020, 9, 30), (2020, 10, 31), (2020, 11, 30),
    (2020, 12, 31), (2000, 2, 29),
]


@pytest.mark.parametrize("y,mo,d", _MONTH_ENDS)
def test_month_end_sweep(y, mo, d):
    assert start_end(_fmt(y, mo, d)) == _day_span(y, mo, d)
