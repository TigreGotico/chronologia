# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Aragonese."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2018 if date(2018, m, d) >= _AD else 2019


@pytest.mark.parametrize("text,m,d", [
    ("5 de chunyo", 6, 5), ("4 de chuliol", 7, 4), ("1 de chinero", 1, 1),
    ("25 de deciembre", 12, 25), ("3 de marzo", 3, 3), ("11 de noviembre", 11, 11),
    ("30 de chunyo", 6, 30), ("14 de febrero", 2, 14), ("9 de setiembre", 9, 9),
    ("5 de mayo", 5, 5), ("23 d'abril", 4, 23), ("12 d'octubre", 10, 12),
    ("15 d'agosto", 8, 15), ("28 d'octubre", 10, 28)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 de chunyo de 2027", 2027, 6, 5), ("20 de chuliol de 1969", 1969, 7, 20),
    ("1 de chinero de 2000", 2000, 1, 1), ("11 de setiembre de 2001", 2001, 9, 11),
    ("12 d'octubre de 1492", 1492, 10, 12), ("6 d'agosto de 1945", 1945, 8, 6),
    ("29 de febrero de 2020", 2020, 2, 29), ("23 d'abril de 1616", 1616, 4, 23)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("chunyo de 2027", 2027, 6), ("chinero de 2020", 2020, 1),
    ("deciembre de 1999", 1999, 12), ("marzo de 2010", 2010, 3),
    ("agosto de 1991", 1991, 8)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("chunyo", 6), ("chinero", 1), ("deciembre", 12), ("marzo", 3),
    ("setiembre", 9), ("agosto", 8)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2018, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1808])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
