"""Russian clock times: digit clocks and the "N часов <meridiem>" form.

Half-convention finding: colloquial Russian tells half hours *forward to* the
next hour -- "полдесятого" / "половина десятого" ("half of the tenth") is
9:30, a half-TO idiom like German "halb zehn".  It is a single word (or
half + genitive ordinal) with no explicit direction token, so the engine's
FRACTION+CLOCKDIR clock cannot express it; recorded as a gap
(test_nl_adversarial).  Digit and "часов"-anchored times are covered here.
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
    ("18:45", 18, 45, 0), ("14:30", 14, 30, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


# "N часов утра/дня/вечера/ночи": genitive-of-day meridiems
@pytest.mark.parametrize("text,h", [
    ("3 часа дня", 15), ("7 часов вечера", 19), ("9 часов утра", 9),
    ("11 часов вечера", 23), ("6 часов утра", 6), ("2 часа дня", 14),
])
def test_hour_meridiem(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("полдень", 12, 0), ("полночь", 0, 0),
])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


def test_bare_1500_is_a_year():
    assert start("1500").year == 1500
