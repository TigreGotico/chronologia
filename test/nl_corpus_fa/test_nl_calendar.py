# -*- coding: utf-8 -*-
"""Gregorian (میلادی) calendar dates in Persian."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


@pytest.mark.parametrize("text,m,d", [
    ("5 ژوئن", 6, 5), ("4 ژوئیه", 7, 4), ("1 ژانویه", 1, 1),
    ("25 دسامبر", 12, 25), ("3 مارس", 3, 3), ("11 نوامبر", 11, 11),
    ("30 ژوئن", 6, 30), ("14 فوریه", 2, 14), ("9 سپتامبر", 9, 9),
    ("21 مارس", 3, 21), ("22 سپتامبر", 9, 22), ("13 اکتبر", 10, 13)])
def test_greg_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 ژوئن 2027", 2027, 6, 5), ("20 ژوئیه 1969", 1969, 7, 20),
    ("1 ژانویه 2000", 2000, 1, 1), ("11 سپتامبر 2001", 2001, 9, 11),
    ("29 فوریه 2028", 2028, 2, 29), ("25 دسامبر 2025", 2025, 12, 25)])
def test_greg_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


@pytest.mark.parametrize("text,y,m", [
    ("ژوئن 2027", 2027, 6), ("ژانویه 2020", 2020, 1),
    ("دسامبر 1999", 1999, 12), ("مارس 2010", 2010, 3)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("ژوئن", 6), ("ژانویه", 1), ("دسامبر", 12), ("مارس", 3)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2017, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1979])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
