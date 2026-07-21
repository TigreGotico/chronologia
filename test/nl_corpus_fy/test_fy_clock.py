"""fy: clock times -- the CONTINENTAL-GERMANIC HALF TRAP centrepiece.

"healwei fiven" == 04:30, the half BEFORE the stated hour -- the opposite of
English "half N" == N:30.  Bare quarter forms are regionally ambiguous and
rejected.  All spans minute-wide; prefer_future rolls a past time to +1 day.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch, clk


@pytest.mark.parametrize("text,h,mi", [('healwei fiven', 4, 30), ('healwei sânen', 6, 30), ('healwei achten', 7, 30), ('healwei tsienen', 9, 30), ('healwei alven', 10, 30), ('healwei tolven', 11, 30), ('healwei ienen', 0, 30), ('healwei twaen', 1, 30), ('healwei trijen', 2, 30), ('healwei fjouweren', 3, 30), ('healwei seizen', 5, 30), ('healwei njoggenen', 8, 30)])
def test_half_is_half_to(text, h, mi):
    assert start(text) == clk(h, mi)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h,mi", [('kertier oer fjouweren', 4, 15), ('kertier foar fiven', 4, 45), ('kertier oer ienen', 1, 15), ('kertier oer tolven', 12, 15), ('kertier foar tolven', 11, 45), ('kertier oer njoggenen', 9, 15), ('kertier foar ienen', 0, 45), ('kertier oer tsienen', 10, 15)])
def test_quarter_explicit(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ['kertier fiven', 'kertier tsienen'])
def test_bare_quarter_rejected(text):
    nomatch(text)


@pytest.mark.parametrize("text,h,mi", [('tweintich oer fjouweren', 4, 20), ('tweintich foar fiven', 4, 40), ('tsien oer fjouweren', 4, 10), ('fiif foar fiven', 4, 55), ('tsien foar tolven', 11, 50)])
def test_minute_to_past(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text,h,mi,s", [
    ("15:30", 15, 30, 0), ("23:59", 23, 59, 0), ("00:00", 0, 0, 0),
    ("09:30", 9, 30, 0), ("18:45", 18, 45, 0),
])
def test_digit_time(text, h, mi, s):
    assert start(text) == clk(h, mi, s)
    assert span(text).width == timedelta(minutes=1)


@pytest.mark.parametrize("text,h", [('fjouwer oere', 4), ('njoggen oere', 9), ('tolve oere', 12), ('om fjouwer', 4), ('om njoggen', 9), ('acht oere', 8), ('om middernacht', 0), ('om middei', 12)])
def test_bare_hour(text, h):
    assert start(text) == clk(h, 0)


@pytest.mark.parametrize("text,h,mi", [('middernacht', 0, 0), ('middei', 12, 0)])
def test_landmark(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23
