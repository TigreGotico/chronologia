# -*- coding: utf-8 -*-
"""Closed ranges (از ... تا ...) and day + daypart combinations.

Ranges resolve to [start-of-first-day, end-of-last-day) with an inclusive last
day, so the end is the day after the closing date.  Gold for the Solar-Hijri
endpoints comes from the independent ``_jalali`` oracle; Gregorian endpoints
are plain calendar arithmetic.

Dayparts on a named day D use fixed windows: صبح = D 01:00-12:00,
عصر = D 12:00-19:00, شب = D 19:00-(D+1) 01:00.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end
from ._jalali import JMON, j2g

GMON = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
        "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]


# ---- Solar-Hijri closed ranges (same month, concordant years) ----
def _sh_ranges():
    out = []
    for y in [1400, 1401, 1402, 1403]:
        for m in [1, 4, 7, 10]:
            for a, b in [(1, 10), (5, 15), (3, 20), (10, 28)]:
                out.append((f"از {a} {JMON[m - 1]} {y} تا {b} {JMON[m - 1]} {y}",
                            y, m, a, b))
    return out


@pytest.mark.parametrize("text,y,m,a,b", _sh_ranges())
def test_solar_hijri_range(text, y, m, a, b):
    s = j2g(y, m, a)
    e = j2g(y, m, b) + timedelta(days=1)
    assert start_end(text) == (ad(datetime(s.year, s.month, s.day)),
                               ad(datetime(e.year, e.month, e.day)))


# ---- Gregorian closed ranges (same month) ----
def _g_ranges():
    out = []
    for y in [2019, 2020, 2021]:
        for m in [1, 5, 9, 12]:
            for a, b in [(1, 10), (5, 15), (3, 20), (10, 25)]:
                out.append((f"از {a} {GMON[m - 1]} {y} تا {b} {GMON[m - 1]} {y}",
                            y, m, a, b))
    return out


@pytest.mark.parametrize("text,y,m,a,b", _g_ranges())
def test_gregorian_range(text, y, m, a, b):
    s = datetime(y, m, a)
    e = datetime(y, m, b) + timedelta(days=1)
    assert start_end(text) == (ad(s), ad(e))


# ---- day + daypart windows ----
_DAY = {"دیروز": -1, "امروز": 0, "فردا": 1}
_PART = {
    "صبح": (1, 12),      # morning
    "عصر": (12, 19),     # afternoon/evening
    "شب": (19, 25),      # night, spills to +1 day 01:00 (25 == +1d 01:00)
}


@pytest.mark.parametrize("day,off", list(_DAY.items()))
@pytest.mark.parametrize("part,h0,h1", [(p, a, b) for p, (a, b) in _PART.items()])
def test_day_daypart(day, off, part, h0, h1):
    base = datetime(2017, 6, 27) + timedelta(days=off)
    s = base + timedelta(hours=h0)
    e = base + timedelta(hours=h1)
    assert start_end(f"{day} {part}") == (ad(s), ad(e))
