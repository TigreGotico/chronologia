# -*- coding: utf-8 -*-
"""``clock_time``'s digital ``CLOCK`` order ("15:30") had no ``at?`` slot at
all, unlike its HOUR-based siblings ("la ora trei"), so the same "la"
preposition strands as remainder in front of a digital reading.

Anchor is the shared ro corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse


def test_la_digit_clock_consumed():
    r = parse("la 20:00")
    assert r is not None
    s, remainder = r
    assert (s.start.year, s.start.month, s.start.day) == (2017, 6, 27)
    assert (s.start.hour, s.start.minute) == (20, 0)
    assert remainder == ""


def test_bare_digit_clock_still_works():
    r = parse("20:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (20, 0)
    assert remainder == ""
