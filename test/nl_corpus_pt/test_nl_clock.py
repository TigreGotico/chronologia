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
    ("às três e meia", 3, 30),
    ("às nove e meia", 9, 30),
    ("às três e quarto", 3, 15),
    ("às nove e quarto", 9, 15),
])
def test_hour_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


# Additive quarter with the explicit numeral: "e um quarto" == the same 15
# minutes past as the bare "e quarto".  The "um" is the article Portuguese
# places before "quarto" (cf. Italian "e un quarto").
# Source: Ciberdúvidas da Língua Portuguesa, "as horas" ("são quatro e um
# quarto").
@pytest.mark.parametrize("text,h,mi", [
    ("quatro e um quarto", 4, 15),
    ("às quatro e um quarto", 4, 15),
    ("nove e um quarto", 9, 15),
])
def test_hour_plus_um_quarto(text, h, mi):
    assert start(text) == clk(h, mi)


# Subtractive clock: "HORA menos ..." counts back from the coming hour --
# "duas menos um quarto" == 1:45, "quatro menos vinte" == 3:40.  Standard
# European Portuguese (native-speaker confirmed); cf. Ciberdúvidas "as horas".
@pytest.mark.parametrize("text,h,mi", [
    ("duas menos um quarto", 1, 45),
    ("às duas menos um quarto", 1, 45),   # was silent-wrong 02:00
    ("quatro menos vinte", 3, 40),
    ("quatro menos dez", 3, 50),
])
def test_hour_minus(text, h, mi):
    assert start(text) == clk(h, mi)


def test_afternoon_meridiem():
    assert start("às três da tarde") == clk(15, 0)


def test_morning_meridiem():
    assert start("às nove da manhã") == clk(9, 0)


def test_noon():
    assert start("meio-dia") == clk(12, 0)


# noon + additive fraction: "meio-dia e meia" == 12:30, exactly as a bare hour
# composes "e meia".  Bare "meio-dia" stays 12:00.
# Source: Ciberdúvidas da Língua Portuguesa ("meio-dia e meia" == 12:30).
@pytest.mark.parametrize("text,h,mi", [
    ("meio-dia e meia", 12, 30), ("meio-dia e quarto", 12, 15),
])
def test_noon_fraction(text, h, mi):
    assert start(text) == clk(h, mi)


def test_midnight():
    assert start("meia-noite") == clk(0, 0)
