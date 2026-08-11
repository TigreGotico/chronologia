# -*- coding: utf-8 -*-
"""Regression for defect R124: the "à" preposition before a bare digital
clock ("à 15h") is stranded as unconsumed remainder on the
``extract_timespan`` path, even though the recurrence path already
consumes it cleanly.

fr's ``clock_time`` grammar leads with "CLOCK article? MERIDIEM? ZONE?" --
no ``at?`` slot -- unlike the HOUR-based orders in the same construction.
The fix adds a mirrored ``at? CLOCK article? MERIDIEM? ZONE?`` order.

Anchor is the shared fr corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from chronologia import extract_recurrence

from ._corpus import ANCHOR, parse


def test_h_clock_at_marker_consumed():
    r = parse("à 15h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("la réunion est à 15h au bureau")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "à" not in remainder.split()


def test_recurrence_still_clean():
    got = extract_recurrence("chaque mardi à 15h", "fr", anchor=ANCHOR)
    assert got is not None
    rule, remainder = got
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=TU;BYHOUR=15"
    assert remainder == ""


def test_generic_preposition_a_survives():
    r = parse("je vais à Paris demain")
    assert r is not None
    s, remainder = r
    assert "je vais à Paris" in remainder
