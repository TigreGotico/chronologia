# -*- coding: utf-8 -*-
"""Closed day-of-month range with an explicit year (ru) -- "с 5 по 12 июня 2020".

Round 1 (``test_ru_day_range_sweep``) swept the bare (prefer-future) reading.
This file pins the explicit-year reading: the span runs [A-th 00:00,
(B+1)-th 00:00) inside the stated month/year, with the (B+1)-th rolling to the
next month via calendar arithmetic.  Gold is that rule applied independently.
Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

# (start-day, end-day) pairs, valid in every month (end <= 27)
_RANGES = [(1, 10), (5, 12), (3, 9), (10, 20), (15, 25), (2, 27)]
_YEARS = (2018, 2019, 2020, 2021)


def _cases():
    out = []
    for m in range(1, 13):
        for a, b in _RANGES:
            for y in _YEARS:
                text = f"с {a} по {b} {_MONTHS_GEN[m]} {y}"
                out.append((text, y, m, a, b))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,y,m,a,b", _CASES, ids=[c[0] for c in _CASES])
def test_day_range_with_year(text, y, m, a, b):
    st, en = start_end(text)
    assert st == AstroDate(y, m, a), text
    end = date(y, m, b) + timedelta(days=1)
    assert en == AstroDate(end.year, end.month, end.day), text
