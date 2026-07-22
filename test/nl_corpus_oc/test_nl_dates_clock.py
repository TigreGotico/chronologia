"""Occitan calendar dates, the h-notation and e-quart/mens-quart clock,
seasons, scoped ordinals, ISO and impossible dates."""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y,m,d", [
    ("15 julhet 2020", 2020, 7, 15),
    ("lo 15 julhet", 2017, 7, 15),
    ("15 julhet", 2017, 7, 15),
    ("1 genièr", 2018, 1, 1),
    ("1èr genièr", 2018, 1, 1),
    ("25 decembre 2021", 2021, 12, 25),
])
def test_calendar_day(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,y,m", [
    ("julhet 2020", 2020, 7),
    ("decembre 1999", 1999, 12),
])
def test_calendar_month(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1)


def test_bare_future_month():
    assert start("decembre") == AstroDate(2017, 12, 1)


def test_iso():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text", ["30 febrièr", "31 abril"])
def test_impossible(text):
    nomatch(text)


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("a 20h", 2017, 6, 27, 20, 0),
    ("20h30", 2017, 6, 27, 20, 30),
    ("a miègjorn", 2017, 6, 28, 12, 0),
    ("a mièjanuèch", 2017, 6, 28, 0, 0),
    ("a tres oras", 2017, 6, 28, 3, 0),
    ("tres oras e quart", 2017, 6, 28, 3, 15),
    ("nòu oras e mièja", 2017, 6, 28, 9, 30),
    ("uèch oras mens quart", 2017, 6, 28, 7, 45),
    ("sèt oras del ser", 2017, 6, 27, 19, 0),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_clock_minute_wide():
    assert span("tres oras e quart").width == timedelta(minutes=1)


@pytest.mark.parametrize("text,sm,em", [
    ("en prima", 3, 6), ("en estiu", 6, 9),
    ("en auton", 9, 12), ("en ivèrn", 12, 3),
])
def test_season(text, sm, em):
    s, e = start_end(text)
    assert (s.month, e.month) == (sm, em)


def test_season_of_year():
    s = start("l'estiu 1969")
    assert (s.year, s.month) == (1969, 6)


@pytest.mark.parametrize("text,y,mo,d,wide", [
    ("la segonda setmana de julhet", 2017, 7, 10, 7),
    ("lo darrièr jorn de julhet", 2017, 7, 31, 1),
])
def test_scoped(text, y, mo, d, wide):
    s, e = start_end(text)
    assert s == AstroDate(y, mo, d)
    assert e - s == timedelta(days=wide)
