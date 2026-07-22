# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Kabyle (day[-n]-month(-year), bare month/year)."""
from datetime import date, timedelta
import pytest
from ._corpus import ANCHOR, AstroDate, start, start_end, span

_AD = ANCHOR.date()


def _fy(m, d):
    return 2017 if date(2017, m, d) >= _AD else 2018


@pytest.mark.parametrize("text,m,d", [
    ("3 yennayer", 1, 3), ("10 fuṛar", 2, 10), ("5 meɣres", 3, 5),
    ("14 yebrir", 4, 14), ("1 mayyu", 5, 1), ("20 yunyu", 6, 20),
    ("4 yulyu", 7, 4), ("6 ɣuct", 8, 6), ("9 ctembeṛ", 9, 9),
    ("12 tubeṛ", 10, 12), ("11 wambeṛ", 11, 11), ("25 dujembeṛ", 12, 25),
    ("3 n yennayer", 1, 3), ("20 n yunyu", 6, 20), ("2 n mayyu", 5, 2),
    ("30 yunyu", 6, 30)])
def test_day_no_year(text, m, d):
    y = _fy(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("3 yennayer 2027", 2027, 1, 3), ("20 yulyu 1969", 1969, 7, 20),
    ("1 yennayer 2000", 2000, 1, 1), ("6 ɣuct 1945", 1945, 8, 6),
    ("25 dujembeṛ 2025", 2025, 12, 25), ("14 yulyu 1789", 1789, 7, 14),
    ("29 fuṛar 2028", 2028, 2, 29), ("11 ctembeṛ 2001", 2001, 9, 11),
    ("1 mayyu 1886", 1886, 5, 1), ("12 tubeṛ 1492", 1492, 10, 12)])
def test_day_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("yunyu 2027", 2027, 6), ("yennayer 2020", 2020, 1),
    ("dujembeṛ 1999", 1999, 12), ("meɣres 2010", 2010, 3),
    ("ɣuct 1991", 1991, 8), ("yulyu 1969", 1969, 7)])
def test_bare_month_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    assert (e - s).days >= 28


@pytest.mark.parametrize("text,m", [
    ("yennayer", 1), ("fuṛar", 2), ("meɣres", 3), ("yebrir", 4),
    ("mayyu", 5), ("yunyu", 6), ("yulyu", 7), ("ɣuct", 8),
    ("ctembeṛ", 9), ("tubeṛ", 10), ("wambeṛ", 11), ("dujembeṛ", 12)])
def test_bare_month(text, m):
    # a bare month name resolves within the anchor year (2017)
    assert start(text) == AstroDate(2017, m, 1)


@pytest.mark.parametrize("y", [1999, 2020, 1969, 1830, 1962, 1954])
def test_bare_year(y):
    s, e = start_end(str(y))
    assert s == AstroDate(y, 1, 1)
    assert e == AstroDate(y + 1, 1, 1)
