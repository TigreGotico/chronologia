# -*- coding: utf-8 -*-
"""Regression for defect R124: the "alle" preposition before a bare
digital clock ("alle 15:00") is stranded as unconsumed remainder on the
``extract_timespan`` path.

it's ``clock_time`` grammar leads with "CLOCK article? MERIDIEM? ZONE?" --
no ``at?`` slot -- unlike the HOUR-based orders in the same construction.
The fix adds a mirrored ``at? CLOCK article? MERIDIEM? ZONE?`` order.

Anchor is the shared it corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse


def test_colon_clock_at_marker_consumed():
    r = parse("alle 15:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("la riunione è alle 15:00 in ufficio")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "alle" not in remainder.split()


def test_generic_preposition_a_survives():
    r = parse("vado a Roma domani")
    assert r is not None
    s, remainder = r
    assert "vado a Roma" in remainder
