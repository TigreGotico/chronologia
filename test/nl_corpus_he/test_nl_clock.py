# -*- coding: utf-8 -*-
"""Clock times: minute-wide spans with the prefer_future roll.  Digit clocks
(with optional בשעה "at hour"), HOUR + day-part word (בבוקר/בערב), and the
noon/midnight landmarks (צהריים/חצות)."""
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
    ("בשעה 15:30", 15, 30), ("בשעה 8:00", 8, 0),
])
def test_digit_time(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [
    ("9 בבוקר", 9), ("7 בבוקר", 7), ("11 בבוקר", 11),
])
def test_morning_meridiem(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h", [
    ("8 בערב", 20), ("9 בערב", 21), ("11 בלילה", 23),
])
def test_evening_meridiem(text, h):
    assert start(text) == clk(h, 0)


# "ba-layla" (at night) is a midnight-crossing BAND, not a uniform +12 PM
# shift: the small hours 1..5 stay AM, the late-night hours 6..11 go PM and
# twelve is midnight 00:00.  AM ceiling follows the CLDR he night band
# [22:00, 06:00) (morning opens at 06:00).  Gold hand-derived, never read
# back from the parser.
@pytest.mark.parametrize("text,h24", [
    ("1 בלילה", 1), ("3 בלילה", 3), ("5 בלילה", 5),
    ("6 בלילה", 18), ("10 בלילה", 22), ("12 בלילה", 0),
])
def test_night_band(text, h24):
    assert start(text) == clk(h24, 0)


def test_noon():
    assert start("צהריים") == clk(12, 0)


def test_midnight():
    assert start("חצות") == clk(0, 0)
