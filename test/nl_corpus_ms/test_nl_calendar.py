# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Malay."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2026 if date(2026, m, d) >= _AD else 2027


@pytest.mark.parametrize("text,m,d", [
    ("5 jun", 6, 5), ("4 julai", 7, 4), ("1 januari", 1, 1),
    ("25 disember", 12, 25), ("3 mac", 3, 3), ("11 november", 11, 11),
    ("30 jun", 6, 30), ("14 februari", 2, 14), ("9 september", 9, 9),
    ("5 mei", 5, 5), ("31 ogos", 8, 31), ("28 oktober", 10, 28),
    ("21 april", 4, 21), ("16 september", 9, 16)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("17 julai 2026", 2026, 7, 17), ("20 julai 1969", 1969, 7, 20),
    ("1 januari 2000", 2000, 1, 1), ("11 september 2001", 2001, 9, 11),
    ("31 ogos 1957", 1957, 8, 31), ("16 september 1963", 1963, 9, 16),
    ("29 februari 2028", 2028, 2, 29), ("31 disember 2026", 2026, 12, 31),
    ("3 mac 2027", 2027, 3, 3), ("21 april 1970", 1970, 4, 21)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("jun 2027", 2027, 6), ("januari 2020", 2020, 1),
    ("disember 1999", 1999, 12), ("mac 2010", 2010, 3),
    ("ogos 1991", 1991, 8)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("jun", 6), ("januari", 1), ("disember", 12), ("mac", 3),
    ("september", 9)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2026, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1957])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
