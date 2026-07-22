# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Arabic: DAY MONTH YEAR, DAY من MONTH YEAR,
MONTH YEAR, bare year.  Both Gregorian-Arabic (يناير) and single/double-token
Levantine (شباط, كانون الثاني) month names."""
import pytest

from ._corpus import AstroDate, start_end, span


@pytest.mark.parametrize("text,s,e", [
    ("15 يناير 2020", (2020, 1, 15), (2020, 1, 16)),
    ("15 من يناير 2020", (2020, 1, 15), (2020, 1, 16)),
    ("20 يوليو 1969", (1969, 7, 20), (1969, 7, 21)),
    ("1 يناير 2000", (2000, 1, 1), (2000, 1, 2)),
    ("9 نوفمبر 1989", (1989, 11, 9), (1989, 11, 10)),
    ("25 ديسمبر 2021", (2021, 12, 25), (2021, 12, 26)),
])
def test_full_dates(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("يناير 2020", (2020, 1, 1), (2020, 2, 1)),
    ("يونيو 2027", (2027, 6, 1), (2027, 7, 1)),
    ("مارس 2020", (2020, 3, 1), (2020, 4, 1)),
    ("أكتوبر 1929", (1929, 10, 1), (1929, 11, 1)),
])
def test_month_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    # Levantine single-token month names
    ("15 شباط 2020", (2020, 2, 15), (2020, 2, 16)),
    ("آذار 2020", (2020, 3, 1), (2020, 4, 1)),
    ("نيسان 2021", (2021, 4, 1), (2021, 5, 1)),
    ("تموز 2019", (2019, 7, 1), (2019, 8, 1)),
])
def test_levantine_single_token(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    # Levantine two-token month names bind via the pipeline multiword merge
    ("كانون الثاني 2020", (2020, 1, 1), (2020, 2, 1)),
    ("تشرين الأول 2020", (2020, 10, 1), (2020, 11, 1)),
    ("تشرين الثاني 2020", (2020, 11, 1), (2020, 12, 1)),
    ("كانون الأول 2020", (2020, 12, 1), (2021, 1, 1)),
])
def test_levantine_two_token(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,y", [
    ("1999", 1999), ("2020", 2020), ("عام 2020", 2020), ("في 1969", 1969),
    ("سنة 1948", 1948),
])
def test_year_ref(text, y):
    ss, ee = start_end(text)
    assert ss == AstroDate(y, 1, 1) and ee == AstroDate(y + 1, 1, 1)
