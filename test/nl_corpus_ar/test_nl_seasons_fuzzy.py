# -*- coding: utf-8 -*-
"""Seasons, fuzzy month thirds (أوائل/منتصف/أواخر), and decades."""
import pytest

from ._corpus import AstroDate, start_end, span


@pytest.mark.parametrize("text,s,e", [
    ("صيف 1969", (1969, 6, 1), (1969, 9, 1)),
    ("شتاء 1970", (1970, 12, 1), (1971, 3, 1)),
    ("ربيع 2000", (2000, 3, 1), (2000, 6, 1)),
    ("خريف 1989", (1989, 9, 1), (1989, 12, 1)),
])
def test_seasons(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,base", [
    ("الثمانينات", 1980), ("التسعينات", 1990), ("الستينات", 1960),
    ("السبعينات", 1970), ("العشرينات", 1920),
])
def test_decades(text, base):
    ss, ee = start_end(text)
    assert ss == AstroDate(base, 1, 1) and ee == AstroDate(base + 10, 1, 1)


@pytest.mark.parametrize("text,month", [
    ("أوائل يناير", 1), ("منتصف يوليو", 7), ("أواخر ديسمبر", 12),
])
def test_month_fuzzy_within(text, month):
    # the fuzzy third stays inside the named month of the anchor year (2017)
    sp = span(text)
    assert sp.start.month == month and sp.start.year == 2017
    assert sp.start < sp.end
