"""Asturian calendar dates, the a-les-N clock with y-cuartu / menos-cuartu
/ y-media fractions, de-la-tarde meridiems, seasons, scoped ordinals."""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y,m,d", [
    ("15 de xunetu 2020", 2020, 7, 15),
    ("el 15 de xunetu", 2017, 7, 15),
    ("15 de xunetu", 2017, 7, 15),
    ("1 de xineru", 2018, 1, 1),
    ("25 d'avientu 2021", 2021, 12, 25),
])
def test_calendar_day(text, y, m, d):
    s, e = start_end(text)
    assert s == AstroDate(y, m, d)
    assert e - s == timedelta(days=1)


def test_bare_future_month():
    assert start("avientu") == AstroDate(2017, 12, 1)


def test_iso():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text", ["30 de febreru", "31 d'abril"])
def test_impossible(text):
    nomatch(text)


@pytest.mark.parametrize("text,y,mo,d,h,mi", [
    ("a les tres", 2017, 6, 28, 3, 0),
    ("a les nueve", 2017, 6, 28, 9, 0),
    ("a mediudía", 2017, 6, 28, 12, 0),
    ("a medianueche", 2017, 6, 28, 0, 0),
    ("a les tres y cuartu", 2017, 6, 28, 3, 15),
    ("les nueve y media", 2017, 6, 28, 9, 30),
    ("a les cuatro menos cuartu", 2017, 6, 28, 3, 45),
    ("a les siete de la tarde", 2017, 6, 27, 19, 0),
    ("a les siete de la mañana", 2017, 6, 28, 7, 0),
])
def test_clock(text, y, mo, d, h, mi):
    assert start(text) == AstroDate(y, mo, d, h, mi)


def test_clock_minute_wide():
    assert span("a les tres y cuartu").width == timedelta(minutes=1)


@pytest.mark.parametrize("text,sm,em", [
    ("en primavera", 3, 6), ("en branu", 6, 9),
    ("en seronda", 9, 12), ("en iviernu", 12, 3),
])
def test_season(text, sm, em):
    s, e = start_end(text)
    assert (s.month, e.month) == (sm, em)


def test_season_of_year():
    s = start("branu 1969")
    assert (s.year, s.month) == (1969, 6)


@pytest.mark.parametrize("text,y,mo,d,wide", [
    ("la segunda selmana de xunetu", 2017, 7, 10, 7),
    ("el últimu día de xunetu", 2017, 7, 31, 1),
])
def test_scoped(text, y, mo, d, wide):
    s, e = start_end(text)
    assert s == AstroDate(y, mo, d)
    assert e - s == timedelta(days=wide)
