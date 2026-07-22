# -*- coding: utf-8 -*-
"""Clock times: minute-wide spans with the prefer_future roll.  Digit clocks
(with optional الساعة "the hour"), HOUR + meridiem day-part word
(صباحا/مساء), and the noon/midnight landmarks."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30), ("23:59", 23, 59), ("09:30", 9, 30),
    ("13:05", 13, 5), ("18:45", 18, 45), ("07:15", 7, 15),
    ("الساعة 15:30", 15, 30), ("الساعة 8:00", 8, 0),
])
def test_digit_time(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [
    ("9 صباحا", 9), ("7 صباحا", 7), ("11 صباحا", 11),
])
def test_morning_meridiem(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h", [
    ("3 مساء", 15), ("8 مساء", 20), ("11 مساء", 23),
])
def test_evening_meridiem(text, h):
    assert start(text) == clk(h, 0)


def test_noon():
    assert start("الظهر") == clk(12, 0)


def test_midnight():
    assert start("منتصف الليل") == clk(0, 0)
