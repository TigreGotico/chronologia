"""Czech clock times: minute-wide spans on the anchor day with the engine's
prefer_future roll.  Digit clocks, the "N ráno/odpoledne/večer" day-part
meridiems, and noon/midnight landmarks.

Half-convention: colloquial Czech tells half hours *forward to* the next hour
-- "půl desáté" ("half of the tenth") is 9:30, a half-TO idiom like German
"halb zehn".  This ordinal-toward-hour clock is covered in
test_cs_toward_clock; explicit digit and day-part times are covered here.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("13:05", 13, 5, 0), ("09:30", 9, 30, 0), ("7:15", 7, 15, 0),
    ("18:45", 18, 45, 0), ("5:07:30", 5, 7, 30), ("14:30", 14, 30, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


# day-part meridiems: ráno/dopoledne -> am, odpoledne/večer -> pm
@pytest.mark.parametrize("text,h", [
    ("3 odpoledne", 15), ("9 ráno", 9), ("8 večer", 20),
    ("11 dopoledne", 11), ("6 ráno", 6), ("10 večer", 22),
])
def test_daypart_meridiem(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30 odpoledne", 15, 30), ("9:30 ráno", 9, 30),
    ("7:45 večer", 19, 45),
])
def test_digit_daypart(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("poledne", 12, 0), ("půlnoc", 0, 0),
])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


def test_compose_date_and_time():
    # 24. prosince 2021 at 18:00
    assert start("24. prosince 2021 18:00") == ad(
        ANCHOR.replace(2021, 12, 24, 18, 0))


# a bare 4-digit run without a leading zero stays a YEAR, not a clock
def test_bare_1500_is_a_year():
    assert start("1500").year == 1500
