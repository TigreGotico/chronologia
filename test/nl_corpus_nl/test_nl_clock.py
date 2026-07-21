"""nl: clock times -- the CONTINENTAL-GERMANIC HALF TRAP centrepiece.

"half negen" == 08:30, the half BEFORE the stated hour -- the opposite of
English "half N" == N:30.  Bare quarter forms are regionally ambiguous and
rejected.  All spans minute-wide; prefer_future rolls a past time to +1 day.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch, clk


@pytest.mark.parametrize("text,h,mi", [('half negen', 8, 30), ('half zeven', 6, 30), ('half acht', 7, 30), ('half tien', 9, 30), ('half elf', 10, 30), ('half twaalf', 11, 30), ('half een', 0, 30), ('half twee', 1, 30), ('half drie', 2, 30), ('half vier', 3, 30), ('half vijf', 4, 30), ('half zes', 5, 30), ('half middag', 11, 30), ('half middernacht', 23, 30)])
def test_half_is_half_to(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h,mi", [('kwart over drie', 3, 15), ('kwart voor negen', 8, 45), ('kwart over elf', 11, 15), ('kwart voor twaalf', 11, 45), ('kwart voor een', 0, 45), ('kwart over middernacht', 0, 15), ('kwart voor middernacht', 23, 45), ('kwart over middag', 12, 15)])
def test_quarter_explicit(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ['kwart negen', 'kwart tien'])
def test_bare_quarter_rejected(text):
    nomatch(text)


@pytest.mark.parametrize("text,h,mi", [('tien voor acht', 7, 50), ('vijf over drie', 3, 5), ('twintig voor zeven', 6, 40), ('vijf voor twaalf', 11, 55), ('tien over middag', 12, 10)])
def test_minute_to_past(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("09:30", 9, 30, 0), ("18:45", 18, 45, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [('om 15', 15), ('om 9', 9), ('om drie', 3), ('15 uur', 15), ('20 uur', 20), ('drie uur', 3), ('acht uur', 8), ('om middernacht', 0), ('om middag', 12)])
def test_bare_hour(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [('middernacht', 0, 0), ('middag', 12, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23
