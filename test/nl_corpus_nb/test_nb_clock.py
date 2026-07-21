"""nb: clock times -- the CONTINENTAL-GERMANIC HALF TRAP centrepiece.

"halv ni" == 08:30, the half BEFORE the stated hour -- the opposite of
English "half N" == N:30.  Bare quarter forms are regionally ambiguous and
rejected.  All spans minute-wide; prefer_future rolls a past time to +1 day.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch, clk


@pytest.mark.parametrize("text,h,mi", [('halv ni', 8, 30), ('halv sju', 6, 30), ('halv åtte', 7, 30), ('halv ti', 9, 30), ('halv elleve', 10, 30), ('halv tolv', 11, 30), ('halv ett', 0, 30), ('halv to', 1, 30), ('halv tre', 2, 30), ('halv fire', 3, 30), ('halv fem', 4, 30), ('halv seks', 5, 30), ('halv middag', 11, 30), ('halv midnatt', 23, 30)])
def test_half_is_half_to(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h,mi", [('kvart over tre', 3, 15), ('kvart på ni', 8, 45), ('kvart over elleve', 11, 15), ('kvart på tolv', 11, 45), ('kvart på ett', 0, 45), ('kvart over midnatt', 0, 15), ('kvart på midnatt', 23, 45), ('kvart over middag', 12, 15)])
def test_quarter_explicit(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ['kvart ni', 'kvart ti'])
def test_bare_quarter_rejected(text):
    nomatch(text)


@pytest.mark.parametrize("text,h,mi", [('ti på åtte', 7, 50), ('fem over tre', 3, 5), ('tjue på sju', 6, 40), ('fem på tolv', 11, 55), ('ti over middag', 12, 10)])
def test_minute_to_past(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("09:30", 9, 30, 0), ("18:45", 18, 45, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [('klokka 15', 15), ('klokka 9', 9), ('klokka tre', 3), ('klokka 20', 20), ('klokka åtte', 8), ('klokka midnatt', 0), ('klokka middag', 12)])
def test_bare_hour(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [('midnatt', 0, 0), ('middag', 12, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23
