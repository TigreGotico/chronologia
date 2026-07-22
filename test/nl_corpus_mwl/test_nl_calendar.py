# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Mirandese."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


@pytest.mark.parametrize("text,m,d", [
    ("5 de júnio", 6, 5), ("4 de júlio", 7, 4), ("1 de janeiro", 1, 1),
    ("25 de dezembre", 12, 25), ("3 de márcio", 3, 3), ("11 de nobembre", 11, 11),
    ("30 de júnio", 6, 30), ("14 de febreiro", 2, 14), ("9 de setembre", 9, 9),
    ("5 de maio", 5, 5), ("23 de abril", 4, 23), ("12 de outubre", 10, 12),
    ("15 de agosto", 8, 15), ("28 de outubre", 10, 28)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 de júnio de 2027", 2027, 6, 5), ("20 de júlio de 1969", 1969, 7, 20),
    ("1 de janeiro de 2000", 2000, 1, 1), ("11 de setembre de 2001", 2001, 9, 11),
    ("12 de outubre de 1492", 1492, 10, 12), ("6 de agosto de 1945", 1945, 8, 6),
    ("29 de febreiro de 2020", 2020, 2, 29), ("25 de dezembre de 2025", 2025, 12, 25)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("júnio de 2027", 2027, 6), ("janeiro de 2020", 2020, 1),
    ("dezembre de 1999", 1999, 12), ("márcio de 2010", 2010, 3),
    ("agosto de 1991", 1991, 8)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("janeiro", 1), ("febreiro", 2), ("márcio", 3), ("abril", 4),
    ("maio", 5), ("júnio", 6), ("júlio", 7), ("agosto", 8),
    ("setembre", 9), ("outubre", 10), ("nobembre", 11), ("dezembre", 12)])
def test_bare_month(text, m):
    assert start(text) == AstroDate(2017, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1580])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
