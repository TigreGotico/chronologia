"""Russian calendar dates: day-month-year order, cardinal day, genitive month
name ("5 июня 2027").  A bare day+month with no year rolls to the next
occurrence (prefer_future) against the 2017-06-27 anchor.
"""
import pytest

from ._corpus import AstroDate, span, start, start_end, parse


@pytest.mark.parametrize("text,y,m,d", [
    ("5 июня 2027", 2027, 6, 5),
    ("15 августа 2020", 2020, 8, 15),
    ("1 января 2000", 2000, 1, 1),
    ("9 мая 1945", 1945, 5, 9),
    ("29 февраля 2020", 2020, 2, 29),
    ("31 декабря 1999", 1999, 12, 31),
    ("12 апреля 1961", 1961, 4, 12),
    ("7 ноября 1917", 1917, 11, 7),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    from datetime import timedelta
    assert span("5 июня 2027").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 августа", 2017, 8, 15),
    ("10 апреля", 2018, 4, 10),
    ("1 января", 2018, 1, 1),
])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_month_year_is_month_wide():
    s, e = start_end("август 2020")
    assert s == AstroDate(2020, 8, 1)
    assert (e.year, e.month) == (2020, 9)


def test_iso_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text,y", [("2019", 2019), ("1945", 1945)])
def test_year(text, y):
    assert start(text) == AstroDate(y, 1, 1)


def test_three_digit_not_a_year():
    r = parse("999")
    assert r is None or r[0].start.year != 999
