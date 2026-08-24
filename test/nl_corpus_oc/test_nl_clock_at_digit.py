# -*- coding: utf-8 -*-
"""``clock_time``'s digital ``CLOCK`` order ("20h", tokenized as a 20:00
clock literal) had no ``at?`` slot at all, unlike its HOUR-based siblings
("a tres oras"), so a leading "a" strands as remainder on the same digital
reading the bare form already resolves cleanly.

Anchor is the shared oc corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse


def test_a_digit_clock_consumed():
    r = parse("a 20h")
    assert r is not None
    s, remainder = r
    assert (s.start.year, s.start.month, s.start.day) == (2017, 6, 27)
    assert (s.start.hour, s.start.minute) == (20, 0)
    assert remainder == ""


def test_bare_digit_clock_still_works():
    r = parse("20h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (20, 0)
    assert remainder == ""
