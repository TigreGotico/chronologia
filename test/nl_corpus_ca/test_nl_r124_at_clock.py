# -*- coding: utf-8 -*-
"""Regression for defect R124: the two-word "a les" preposition before a
bare digital clock ("a les 15:00") is stranded as unconsumed remainder on
the ``extract_timespan`` path.

ca's ``clock_time`` grammar's bare-CLOCK order ("CLOCK MERIDIEM? ZONE?")
has no leading ``at?`` slot, unlike the HOUR-based orders in the same
construction.  The fix adds a mirrored ``at? CLOCK MERIDIEM? ZONE?``
order.

Anchor is the shared ca corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse


def test_two_word_at_marker_consumed():
    r = parse("a les 15:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("la reunió és a les 15:00 a l'oficina")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "a les" not in remainder


def test_generic_preposition_a_survives():
    r = parse("vaig a Barcelona demà")
    assert r is not None
    s, remainder = r
    assert "vaig a Barcelona" in remainder
