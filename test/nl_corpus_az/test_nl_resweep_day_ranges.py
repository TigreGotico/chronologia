# -*- coding: utf-8 -*-
"""Second-pass sweep: day-ranges within a single month, Azerbaijani
``"<N>-<M> <ay> <il>"`` (e.g. "3-9 iyun 2021").  This shape was not covered by
the first-pass corpus (which only swept single dates and month/year spans).

Gold is pure calendar arithmetic: start = day N of the named month/year, end
(exclusive) = day M + 1 of that same month/year.  All (year, month, N, M)
combinations below stay within one calendar month, so no month/year rollover
logic is exercised here.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import start_end

MONTHS = {
    1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel", 5: "may", 6: "iyun",
    7: "iyul", 8: "avqust", 9: "sentyabr", 10: "oktyabr", 11: "noyabr",
    12: "dekabr",
}

# Fresh years, not reused from the first-pass sweep (1912/1945/1969/1991/
# 2008/2019/2023/2031 in test_nl_calendar_sweep.py; 1999/2020/2026/2033 for
# month+year there; 1918/1961/1969/1991/1999/2000/2001/1945/2027/2028 in
# test_nl_calendar.py).
YEARS = [1955, 1978, 1992, 2015, 2021, 2029]

# A short-range and a longer-range pair per month, both safely inside every
# month's valid day count (max start 20, max end 26).
_DAY_PAIRS = [(3, 9), (14, 20)]


def _cases():
    out = []
    for y in YEARS:
        for m in range(1, 13):
            for n, mm in _DAY_PAIRS:
                out.append((y, m, n, mm))
    return out


@pytest.mark.parametrize("y,m,n,mm", _cases())
def test_day_range_within_month(y, m, n, mm):
    txt = "%d-%d %s %d" % (n, mm, MONTHS[m], y)
    s, en = start_end(txt)
    assert s == AstroDate(y, m, n)
    exp_end = date(y, m, mm) + timedelta(days=1)
    assert en == AstroDate(exp_end.year, exp_end.month, exp_end.day)


# ---- a handful spanning a month boundary, to confirm the range clamps to
#      the literal days named rather than snapping to full-month bounds ----
_BOUNDARY = [
    (2021, 1, 28, 31), (2024, 2, 25, 29),  # 2024 is a leap year
    (1978, 4, 27, 30), (2015, 6, 25, 30),
]


@pytest.mark.parametrize("y,m,n,mm", _BOUNDARY)
def test_day_range_near_month_end(y, m, n, mm):
    txt = "%d-%d %s %d" % (n, mm, MONTHS[m], y)
    s, en = start_end(txt)
    assert s == AstroDate(y, m, n)
    exp_end = date(y, m, mm) + timedelta(days=1)
    assert en == AstroDate(exp_end.year, exp_end.month, exp_end.day)
