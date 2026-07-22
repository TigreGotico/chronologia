# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Turkish (day-month(-year), bare month/year)."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2026 if date(2026, m, d) >= _AD else 2027


@pytest.mark.parametrize("text,m,d", [
    ("5 haziran", 6, 5), ("4 temmuz", 7, 4), ("1 ocak", 1, 1),
    ("25 aralık", 12, 25), ("3 mart", 3, 3), ("11 kasım", 11, 11),
    ("30 haziran", 6, 30), ("14 şubat", 2, 14), ("9 eylül", 9, 9),
    ("5 mayıs", 5, 5), ("23 nisan", 4, 23), ("29 ekim", 10, 29),
    ("19 mayıs", 5, 19), ("30 ağustos", 8, 30)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 haziran 2027", 2027, 6, 5), ("20 temmuz 1969", 1969, 7, 20),
    ("1 ocak 2000", 2000, 1, 1), ("11 eylül 2001", 2001, 9, 11),
    ("29 ekim 1923", 1923, 10, 29), ("6 ağustos 1945", 1945, 8, 6),
    ("29 şubat 2028", 2028, 2, 29), ("26 temmuz 2026", 2026, 7, 26),
    ("23 nisan 1920", 1920, 4, 23), ("30 ağustos 1922", 1922, 8, 30)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("haziran 2027", 2027, 6), ("ocak 2020", 2020, 1),
    ("aralık 1999", 1999, 12), ("mart 2010", 2010, 3),
    ("ağustos 1991", 1991, 8)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("haziran", 6), ("ocak", 1), ("aralık", 12), ("mart", 3), ("eylül", 9)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2026, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1923])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
