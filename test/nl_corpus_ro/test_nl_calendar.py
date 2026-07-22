"""Romanian calendar dates, ISO literals, impossible-date rejection."""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y,m,d", [
    ("15 iulie 2020", 2020, 7, 15),
    ("pe 15 iulie 2020", 2020, 7, 15),
    ("15 iulie", 2017, 7, 15),
    ("3 martie 2019", 2019, 3, 3),
    ("1 ianuarie", 2018, 1, 1),
    ("25 decembrie 2021", 2021, 12, 25),
    ("1 decembrie 1918", 1918, 12, 1),
    ("pe 15 iulie", 2017, 7, 15),
])
def test_calendar_day(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("iulie 2020", 2020, 7),
    ("septembrie 2019", 2019, 9),
    ("decembrie 1999", 1999, 12),
    ("august 1969", 1969, 8),
])
def test_calendar_month(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1)
    assert span(text).width >= timedelta(days=28)


def test_bare_future_month():
    assert start("decembrie") == AstroDate(2017, 12, 1)


def test_iso_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text", [
    "30 februarie", "31 aprilie", "30 februarie 2020", "31 aprilie 2020",
])
def test_impossible_dates(text):
    nomatch(text)


def test_valid_date_in_sentence():
    assert start("întâlnire pe 15 iulie 2020 la birou") == AstroDate(2020, 7, 15)
