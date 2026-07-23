"""Hungarian clock times.  The traditional spoken clock counts TOWARD the
coming hour: "fél kilenc" is 8:30 (half before nine) -- the half-to family,
handled by the bare_half_to convention.  Digit times, the délben/éjfél
landmarks and "H óra" whole hours are also asserted.

The quarter/three-quarter counting forms ("negyed kilenc" 8:15,
"háromnegyed kilenc" 8:45) run the same counting-toward-the-hour system as
the half (bare_quarter_to convention) and are asserted directly.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, nomatch


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("fél kilenc", 8, 30),
    ("fél nyolc", 7, 30),
    ("fél tizenkettő", 11, 30),
    ("fél tíz", 9, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h", [
    ("kilenc óra", 9),
    ("tíz óra", 10),
    ("nyolc óra", 8),
])
def test_whole_hour(text, h):
    assert start(text) == _next_time(h, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30),
    ("09:15", 9, 15),
    ("23:45", 23, 45),
    ("00:00", 0, 0),
])
def test_digit_clock(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("délben", 12, 0),
    ("éjfél", 0, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("negyed kilenc", 8, 15),       # a quarter toward nine
    ("háromnegyed kilenc", 8, 45),  # three quarters toward nine
    ("negyed tíz", 9, 15),
    ("háromnegyed tizenkettő", 11, 45),
    ("negyed nyolc", 7, 15),
])
def test_quarter_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text", [
    "negyed",           # bare fraction, no hour -- must not crash or resolve
    "háromnegyed",
])
def test_bare_fraction_without_hour_is_not_a_clock(text):
    # A fraction word with no hour to count toward is not a clock reading;
    # the engine must decline it, not raise.
    nomatch(text)
