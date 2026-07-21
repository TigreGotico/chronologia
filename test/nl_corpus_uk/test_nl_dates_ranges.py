"""Ukrainian calendar dates, ranges, seasons, clock.

Dates run day-month-year with a genitive month ("15 серпня 2020").  Ranges use
з/до and між/і over instrumental month forms.  Seasons are meteorological,
northern hemisphere.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 серпня 2020", 2020, 8, 15),
    ("1 січня 2000", 2000, 1, 1),
    ("24 серпня 1991", 1991, 8, 24),
    ("29 лютого 2020", 2020, 2, 29),
    ("22 січня 1919", 1919, 1, 22),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15 серпня 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 серпня", 2017, 8, 15),
    ("10 квітня", 2018, 4, 10),
])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("з червня до серпня", "2017-6-1", "2017-9-1"),
    ("з січня до березня", "2017-1-1", "2017-4-1"),
    ("з жовтня до грудня", "2017-10-1", "2018-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("між червнем і вереснем", "2017-6-1", "2017-10-1"),
    ("між квітнем і червнем", "2017-4-1", "2017-7-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("наступна зима", "2017-12-1", "2018-3-1"),
    ("літо 2020", "2020-6-1", "2020-9-1"),
    ("зима 2019", "2019-12-1", "2020-3-1"),
])
def test_season(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


def clk(h, mi):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("00:00", 0, 0), ("09:30", 9, 30), ("23:59", 23, 59),
])
def test_digit_time(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h,mi", [("полудень", 12, 0), ("північ", 0, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)
