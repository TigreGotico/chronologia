# -*- coding: utf-8 -*-
"""Slovak full day-month-year dates: "15. augusta 2020".

Slovak writes a calendar date day-first, the day as an ordinal (dot) and the
month in the genitive: "15. augusta 2020", "1. januára 2000", "29. februára
2020".  The span is exactly that single day, 00:00 to 00:00 the next day.
Expected bounds are one day of ``datetime`` arithmetic, never the parser.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

#: genitive month names, index 1..12.
_GEN = [None, "januára", "februára", "marca", "apríla", "mája", "júna",
        "júla", "augusta", "septembra", "októbra", "novembra", "decembra"]


def _day(y, m, d):
    from datetime import date, timedelta
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(y, m, d), AstroDate(nxt.year, nxt.month, nxt.day)


# (day, month) pairs valid in every listed year; day chosen to exercise the
# whole month range without hitting a short-month overflow.
_DM = [(1, 1), (15, 1), (31, 1), (8, 2), (28, 2), (3, 3), (17, 3), (30, 3),
       (10, 4), (25, 4), (1, 5), (15, 5), (31, 5), (5, 6), (30, 6), (7, 7),
       (24, 7), (15, 8), (30, 8), (9, 9), (20, 9), (12, 10), (31, 10),
       (3, 11), (28, 11), (6, 12), (25, 12), (31, 12)]

_YEARS = [2000, 2010, 2018, 2019, 2020, 2021, 2023, 2025]


@pytest.mark.parametrize("year", _YEARS)
@pytest.mark.parametrize("d,m", _DM)
def test_dmy(d, m, year):
    text = f"{d}. {_GEN[m]} {year}"
    assert start_end(text) == _day(year, m, d), text


def test_leap_day_2020():
    """29 February exists only in a leap year; the parser reads the real day."""
    assert start_end("29. februára 2020") == _day(2020, 2, 29)
