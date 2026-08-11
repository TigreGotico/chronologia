# -*- coding: utf-8 -*-
"""Regression for defect R124: the "ás" preposition before a bare digital
clock ("ás 15:00") is stranded as unconsumed remainder on the
``extract_timespan`` path.

gl's ``clock_time`` grammar's bare-CLOCK order ("CLOCK MERIDIEM? ZONE?")
has no leading ``at?`` slot, unlike the HOUR-based orders in the same
construction.  The fix adds a mirrored ``at? CLOCK MERIDIEM? ZONE?``
order.

Anchor is the shared gl corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from chronologia import extract_recurrence

from ._corpus import ANCHOR, parse


def test_colon_clock_at_marker_consumed():
    r = parse("ás 15:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("a reunión é ás 15:00 na oficina")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "ás" not in remainder.split()


def test_recurrence_still_clean():
    got = extract_recurrence("cada martes ás 15:00", "gl", anchor=ANCHOR)
    assert got is not None
    rule, remainder = got
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=TU;BYHOUR=15"
    assert remainder == ""


def test_generic_preposition_a_survives():
    r = parse("vou a Lugo mañá")
    assert r is not None
    s, remainder = r
    assert "vou a Lugo" in remainder
