# -*- coding: utf-8 -*-
"""Clock times: minute-wide spans with the prefer_future roll.  Digit clocks
(with optional الساعة "the hour"), HOUR + meridiem day-part word
(صباحا/مساء), and the noon/midnight landmarks."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, remainder, start, span


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


# -- spoken clock fractions: HOUR-then-CLOCKDIR-then-FRACTION -----------------
# Arabic hangs the fraction off the hour with the glued "و" (and, past) or the
# spaced "إلا" (less, to): "الثالثة والنصف" == 03:30 (mirror of "half past
# three"), "العاشرة والربع" == 10:15, "الواحدة إلا ربع" == 00:45.
@pytest.mark.parametrize("text,h,mi", [
    ("الساعة الثالثة والنصف", 3, 30),
    ("الساعة العاشرة والربع", 10, 15),
    ("الساعة الثامنة والنصف", 8, 30),
    ("الساعة الواحدة الا ربع", 0, 45),
    ("الساعة الثانية إلا ربع", 1, 45),
])
def test_clock_fraction(text, h, mi):
    assert start(text) == clk(h, mi)
    assert remainder(text) == ""


# the day-part particle still shifts the fractional reading across noon.
@pytest.mark.parametrize("text,h,mi", [
    ("الساعة الثالثة والنصف صباحا", 3, 30),
    ("الساعة الثالثة والنصف مساء", 15, 30),
    ("الساعة العاشرة والربع مساء", 22, 15),
])
def test_clock_fraction_meridiem(text, h, mi):
    assert start(text) == clk(h, mi)


# a bare hour with no fraction is unchanged.
def test_clock_hour_no_fraction():
    assert start("الساعة الثالثة") == clk(3, 0)
