"""French calendar dates: every field order the engine accepts, the "1er"
first-of-month ordinal, ISO literals, and impossible-date rejection.

Hand-derived against the Tuesday 2017-06-27 anchor; a day-only date is
day-wide, a month-only date is month-wide, a year-only reference is
year-wide.
"""
from datetime import timedelta

import pytest

from ._corpus import ad, span, start, start_end, nomatch, AstroDate


# -- day / month / year, all orders (day-wide) ----------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15 juillet 2020", 2020, 7, 15),
    ("le 15 juillet 2020", 2020, 7, 15),
    ("15 juillet", 2017, 7, 15),
    ("le 3 mars 2019", 2019, 3, 3),
    ("3 mars 2019", 2019, 3, 3),
    ("1er janvier", 2018, 1, 1),
    ("le 1er janvier", 2018, 1, 1),
    ("le premier mai", 2018, 5, 1),
    ("25 décembre 2021", 2021, 12, 25),
    ("14 juillet 1789", 1789, 7, 14),
    ("8 mai 1945", 1945, 5, 8),
])
def test_calendar_day(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e - s == timedelta(days=1)


# -- month + year (month-wide) --------------------------------------------

@pytest.mark.parametrize("text,y,m", [
    ("juillet 2020", 2020, 7),
    ("en mars 2019", 2019, 3),
    ("décembre 1999", 1999, 12),
    ("août 1969", 1969, 8),
])
def test_calendar_month(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1)
    assert span(text).width >= timedelta(days=28)


# -- bare month rolls to the next occurrence (future-preferring) ----------

def test_bare_future_month():
    assert start("décembre") == AstroDate(2017, 12, 1)


# -- ISO literal ----------------------------------------------------------

def test_iso_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


# -- impossible dates never parse -----------------------------------------

@pytest.mark.parametrize("text", [
    "30 février", "31 avril", "30 février 2020", "février 30", "31 avril 2020",
])
def test_impossible_dates(text):
    nomatch(text)


def test_valid_date_in_sentence():
    assert start("rendez-vous le 15 juillet 2020 au bureau") == AstroDate(2020, 7, 15)
