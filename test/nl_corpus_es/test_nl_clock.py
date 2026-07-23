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
    ("las tres y media", 3, 30),
    ("las nueve y media", 9, 30),
    ("las tres y cuarto", 3, 15),
    ("las nueve y cuarto", 9, 15),
])
def test_hour_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


# Subtractive minutes: "las HORA menos MINUTE" counts back from the coming
# hour, exactly as the quarter does -- "las diez menos veinte" == 9:40.  The
# pattern generalises past the quarter to any minute count.
# Source: RAE, Diccionario panhispánico de dudas, "hora": «las diez menos
# veinte» = 9:40.
@pytest.mark.parametrize("text,h,mi", [
    ("las cuatro menos veinte", 3, 40),
    ("las diez menos veinte", 9, 40),
    ("las cuatro menos diez", 3, 50),
    ("las dos menos cuarto", 1, 45),      # fraction path unchanged
])
def test_hour_minus_minutes(text, h, mi):
    assert start(text) == clk(h, mi)


def test_bare_hour_unchanged():
    # adversarial: the bare hour must not absorb a phantom offset.
    assert start("las cuatro") == clk(4, 0)


def test_afternoon_meridiem():
    assert start("las tres de la tarde") == clk(15, 0)


def test_morning_meridiem():
    assert start("las nueve de la mañana") == clk(9, 0)


def test_noon():
    assert start("mediodía") == clk(12, 0)


# noon + additive fraction: "mediodía y media" == 12:30, exactly as a bare hour
# composes "y media" (half past).  Bare "mediodía" stays 12:00.
# Source: RAE, Diccionario, "y media" (la una y media, mediodía y media).
@pytest.mark.parametrize("text,h,mi", [
    ("mediodía y media", 12, 30), ("mediodia y media", 12, 30),
    ("mediodía y cuarto", 12, 15),
])
def test_noon_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


def test_midnight():
    assert start("medianoche") == clk(0, 0)
