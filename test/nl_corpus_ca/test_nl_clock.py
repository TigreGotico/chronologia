# -*- coding: utf-8 -*-
"""Clock times: minute-wide spans with the prefer_future roll."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("09:30", 9, 30, 0),
    ("13:05", 13, 5, 0), ("18:45", 18, 45, 0), ("07:15", 7, 15, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h,mi", [
    ("les tres i mitja", 3, 30),
    ("les nou i mitja", 9, 30),
    ("les tres i quart", 3, 15),
    ("les nou i quart", 9, 15),
])
def test_hour_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


def test_afternoon_meridiem():
    assert start("les tres de la tarda") == clk(15, 0)


def test_morning_meridiem():
    assert start("les nou del matí") == clk(9, 0)


def test_noon():
    assert start("migdia") == clk(12, 0)


def test_midnight():
    assert start("mitjanit") == clk(0, 0)
