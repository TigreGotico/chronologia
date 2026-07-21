# -*- coding: utf-8 -*-
"""Gregorian calendar dates: day-month(-year), bare month, bare year."""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, start, start_end, span, nomatch

_ANCHOR_DAY = ANCHOR.date()


def _future_year(m, d):
    return 2017 if date(2017, m, d) >= _ANCHOR_DAY else 2018


@pytest.mark.parametrize("text,m,d", [("5 de junio", 6, 5), ("4 de julio", 7, 4), ("1 de enero", 1, 1), ("25 de diciembre", 12, 25), ("3 de marzo", 3, 3), ("11 de noviembre", 11, 11), ("30 de junio", 6, 30), ("14 de febrero", 2, 14), ("9 de septiembre", 9, 9), ("5 de mayo", 5, 5)])
def test_day_no_year(text, m, d):
    y = _future_year(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [("5 de junio de 2027", 2027, 6, 5), ("20 de julio de 1969", 1969, 7, 20), ("1 de enero de 2000", 2000, 1, 1), ("11 de septiembre de 2001", 2001, 9, 11), ("14 de julio de 1789", 1789, 7, 14), ("6 de agosto de 1945", 1945, 8, 6), ("12 de octubre de 1492", 1492, 10, 12), ("29 de febrero de 2020", 2020, 2, 29)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [("junio de 2027", 2027, 6), ("enero de 2020", 2020, 1), ("diciembre de 1999", 1999, 12), ("marzo de 2010", 2010, 3)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [("junio", 6), ("enero", 1), ("diciembre", 12), ("marzo", 3), ("septiembre", 9)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2017, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 44 + 1900])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
