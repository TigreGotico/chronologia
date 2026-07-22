"""Italian calendar dates, ISO literals, and impossible-date rejection."""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y,m,d", [
    ("15 luglio 2020", 2020, 7, 15),
    ("il 15 luglio 2020", 2020, 7, 15),
    ("15 luglio", 2017, 7, 15),
    ("il quindici luglio", 2017, 7, 15),
    ("3 marzo 2019", 2019, 3, 3),
    ("1 gennaio", 2018, 1, 1),
    ("il 1 gennaio", 2018, 1, 1),
    ("25 dicembre 2021", 2021, 12, 25),
    ("2 giugno 1946", 1946, 6, 2),
    ("il 15 luglio", 2017, 7, 15),
])
def test_calendar_day(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("luglio 2020", 2020, 7),
    ("marzo 2019", 2019, 3),
    ("dicembre 1999", 1999, 12),
    ("agosto 1969", 1969, 8),
])
def test_calendar_month(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1)
    assert span(text).width >= timedelta(days=28)


def test_bare_future_month():
    assert start("dicembre") == AstroDate(2017, 12, 1)


def test_iso_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text", [
    "30 febbraio", "31 aprile", "30 febbraio 2020", "febbraio 30", "31 aprile 2020",
])
def test_impossible_dates(text):
    nomatch(text)


def test_valid_date_in_sentence():
    assert start("appuntamento il 15 luglio 2020 in ufficio") == AstroDate(2020, 7, 15)
