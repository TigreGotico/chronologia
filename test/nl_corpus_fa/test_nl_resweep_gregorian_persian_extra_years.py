# -*- coding: utf-8 -*-
"""Second-pass resweep: Gregorian dates with Persian Gregorian month names,
extended to years NOT covered by ``test_nl_sweep_gregorian.py`` (which only
swept 2018-2022).  Gold is the plain Gregorian calendar, independent of the
engine.
"""
import pytest

from ._corpus import ad, start, start_end, AstroDate

GMON = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
        "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]

_YEARS = [2023, 2024, 2025, 2026]
_DAYS = [1, 10, 20, 28]


@pytest.mark.parametrize("text,y,m,d", [
    (f"{d} {GMON[m - 1]} {y}", y, m, d)
    for y in _YEARS for m in range(1, 13) for d in _DAYS
])
def test_gregorian_full_date_extra_years(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m", [
    (f"{GMON[m - 1]} {y}", y, m) for y in _YEARS for m in range(1, 13)
])
def test_gregorian_month_year_span_extra_years(text, y, m):
    from datetime import date
    s = date(y, m, 1)
    e = date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    from datetime import datetime
    assert start_end(text) == (ad(datetime(s.year, s.month, s.day)),
                               ad(datetime(e.year, e.month, e.day)))
