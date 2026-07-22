# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Azerbaijani."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


@pytest.mark.parametrize("text,m,d", [
    ("5 iyun", 6, 5), ("4 iyul", 7, 4), ("1 yanvar", 1, 1),
    ("25 dekabr", 12, 25), ("3 mart", 3, 3), ("11 noyabr", 11, 11),
    ("30 iyun", 6, 30), ("14 fevral", 2, 14), ("9 sentyabr", 9, 9),
    ("5 may", 5, 5), ("28 may", 5, 28), ("18 oktyabr", 10, 18),
    ("12 aprel", 4, 12), ("8 avqust", 8, 8)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 iyun 2027", 2027, 6, 5), ("20 iyul 1969", 1969, 7, 20),
    ("1 yanvar 2000", 2000, 1, 1), ("11 sentyabr 2001", 2001, 9, 11),
    ("28 may 1918", 1918, 5, 28), ("6 avqust 1945", 1945, 8, 6),
    ("29 fevral 2028", 2028, 2, 29), ("18 oktyabr 1991", 1991, 10, 18),
    ("12 aprel 1961", 1961, 4, 12), ("31 dekabr 1999", 1999, 12, 31)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("iyun 2027", 2027, 6), ("yanvar 2020", 2020, 1),
    ("dekabr 1999", 1999, 12), ("mart 2010", 2010, 3),
    ("avqust 1991", 1991, 8)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("iyun", 6), ("yanvar", 1), ("dekabr", 12), ("mart", 3), ("sentyabr", 9)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2017, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1918])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
