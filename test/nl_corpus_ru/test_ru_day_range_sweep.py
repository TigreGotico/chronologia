# -*- coding: utf-8 -*-
"""Closed day-of-month range sweep (ru) -- "с 5 по 12 июня".

"с A по B <month>" is an inclusive day-range within one month; the parsed span
runs [A-th 00:00, (B+1)-th 00:00).  With no explicit year the engine resolves
to the next occurrence: it keeps the anchor year when the last included day is
still on or after the anchor date, else rolls to the following year.  Gold is
that rule applied by independent arithmetic.  Anchor 2017-06-27 (a Tuesday)."""
from datetime import date

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_ANCHOR = date(2017, 6, 27)
# (start-day, end-day) pairs, valid in every swept month
_RANGES = [(1, 10), (5, 12), (3, 9), (10, 20), (15, 25), (2, 27)]
_MONTHS = range(1, 13)


def _year_for(month, last_day):
    """Next-occurrence year: keep 2017 if last included day >= anchor."""
    if date(2017, month, last_day) >= _ANCHOR:
        return 2017
    return 2018


def _cases():
    out = []
    for month in _MONTHS:
        for a, b in _RANGES:
            year = _year_for(month, b)
            text = f"с {a} по {b} {_MONTHS_GEN[month]}"
            out.append((text, year, month, a, b))
    return out


@pytest.mark.parametrize("text,y,m,a,b", _cases())
def test_day_range(text, y, m, a, b):
    st, en = start_end(text)
    assert st == AstroDate(y, m, a)
    # inclusive end -> exclusive (b+1)-th; end-of-month rolls via timedelta
    from datetime import datetime, timedelta
    exp_end = datetime(y, m, b) + timedelta(days=1)
    assert en == AstroDate(exp_end.year, exp_end.month, exp_end.day)


@pytest.mark.xfail(reason="'с A по B <month> <year>' mis-parses: the explicit "
                          "year is not bound to the range and residue leaks "
                          "('5 по'). No-year form is correct. BUG, deferred.",
                   strict=True)
def test_day_range_with_year_broken():
    st, en = start_end("с 5 по 12 июня 2019")
    assert st == AstroDate(2019, 6, 5)
    assert en == AstroDate(2019, 6, 13)
