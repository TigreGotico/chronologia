# -*- coding: utf-8 -*-
"""Locale-agnostic date literals in Kabyle: ISO-8601 (YYYY-MM-DD) and
numeric day/month/year (DD/MM/YYYY, dmy per lang.json). Each resolves to the
exact single day regardless of language; gold is the literal date, width 1 day.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start, start_end

# (y, m, d) -- each rendered as ISO and as slash-dmy
_DATES = [
    (2017, 6, 27), (2000, 1, 1), (1999, 12, 31), (2028, 2, 29),
    (1945, 8, 6), (2024, 2, 29), (1789, 7, 14), (1969, 7, 20),
    (2020, 1, 1), (1492, 10, 12),
]


def _next_day(y, m, d):
    nxt = date(y, m, d) + timedelta(days=1)
    return AstroDate(nxt.year, nxt.month, nxt.day)


@pytest.mark.parametrize("y,m,d", _DATES)
def test_iso_date(y, m, d):
    text = "%04d-%02d-%02d" % (y, m, d)
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e == _next_day(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("y,m,d", _DATES)
def test_numeric_dmy(y, m, d):
    text = "%02d/%02d/%04d" % (d, m, y)
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e == _next_day(y, m, d)
    assert span(text).width == timedelta(days=1)
