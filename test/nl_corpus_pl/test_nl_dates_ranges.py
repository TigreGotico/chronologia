"""Polish calendar dates, ranges, seasons, clock.

Dates run day-month-year with a genitive month ("15 sierpnia 2020").  Ranges
use od/do and między/a over instrumental month forms.  Seasons are
meteorological, northern hemisphere.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 sierpnia 2020", 2020, 8, 15),
    ("1 stycznia 2000", 2000, 1, 1),
    ("3 maja 1791", 1791, 5, 3),
    ("29 lutego 2020", 2020, 2, 29),
    ("11 listopada 1918", 1918, 11, 11),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15 sierpnia 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 sierpnia", 2017, 8, 15),
    ("10 kwietnia", 2018, 4, 10),
])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("od czerwca do sierpnia", "2017-6-1", "2017-9-1"),
    ("od stycznia do marca", "2017-1-1", "2017-4-1"),
    ("od października do grudnia", "2017-10-1", "2018-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("między czerwcem a wrześniem", "2017-6-1", "2017-10-1"),
    ("między kwietniem a czerwcem", "2017-4-1", "2017-7-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("przyszła zima", "2017-12-1", "2018-3-1"),
    ("lato 2020", "2020-6-1", "2020-9-1"),
    ("zima 2019", "2019-12-1", "2020-3-1"),
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


@pytest.mark.parametrize("text,h,mi", [("południe", 12, 0), ("północ", 0, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)
