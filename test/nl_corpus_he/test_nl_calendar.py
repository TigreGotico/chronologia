# -*- coding: utf-8 -*-
"""Gregorian calendar dates in Hebrew: the month takes a ב- prefix in a full
date ("15 בינואר 2020") and stands bare in a month-year ("ינואר 2020")."""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,s,e", [
    ("15 בינואר 2020", (2020, 1, 15), (2020, 1, 16)),
    ("20 ביולי 1969", (1969, 7, 20), (1969, 7, 21)),
    ("1 בינואר 2000", (2000, 1, 1), (2000, 1, 2)),
    ("9 בנובמבר 1989", (1989, 11, 9), (1989, 11, 10)),
    ("25 בדצמבר 2021", (2021, 12, 25), (2021, 12, 26)),
    ("5 במאי 2018", (2018, 5, 5), (2018, 5, 6)),
])
def test_full_dates(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("ינואר 2020", (2020, 1, 1), (2020, 2, 1)),
    ("יוני 2027", (2027, 6, 1), (2027, 7, 1)),
    ("מרץ 2020", (2020, 3, 1), (2020, 4, 1)),
    ("אוקטובר 1929", (1929, 10, 1), (1929, 11, 1)),
    ("ספטמבר 2001", (2001, 9, 1), (2001, 10, 1)),
])
def test_month_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,y", [
    ("1999", 1999), ("2020", 2020), ("שנת 2020", 2020),
    ("בשנת 1948", 1948), ("שנת 1967", 1967),
])
def test_year_ref(text, y):
    ss, ee = start_end(text)
    assert ss == AstroDate(y, 1, 1) and ee == AstroDate(y + 1, 1, 1)
