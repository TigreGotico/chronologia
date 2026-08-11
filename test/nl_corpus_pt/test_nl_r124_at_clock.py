# -*- coding: utf-8 -*-
"""Regression for defect R124: the "at" preposition before a bare digital
clock ("às 15:00", "às 15h") is consumed on the recurrence path but
stranded as unconsumed remainder on the plain ``extract_timespan`` path.

The pt ``clock_time`` grammar's bare-CLOCK order ("CLOCK MERIDIEM? ZONE?")
has no leading ``at?`` slot, unlike the HOUR-based orders in the same
construction (which all start with ``at?``).  So "às 15:00" resolves the
clock literal but leaves "às" dangling.  The fix adds a mirrored
``at? CLOCK MERIDIEM? ZONE?`` order, exactly like ``ar``/``he`` already do
for the same construction.

Anchor is the shared pt corpus anchor, 2017-06-27 13:04 (Tuesday) -- see
``test/nl_corpus_pt/_corpus.py``.
"""
from chronologia import extract_recurrence

from ._corpus import ANCHOR, parse


def test_colon_clock_at_marker_consumed():
    r = parse("às 15:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_h_clock_at_marker_consumed():
    r = parse("às 15h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("a reunião é às 15:00 no escritório")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "às" not in remainder.split()


def test_recurrence_still_clean():
    got = extract_recurrence("toda terça às 15h", "pt", anchor=ANCHOR)
    assert got is not None
    rule, remainder = got
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=TU;BYHOUR=15"
    assert remainder == ""


def test_generic_preposition_a_survives():
    # "a" as a plain preposition ("to") before a place must not be eaten
    # just because a clock construction exists in the grammar.
    r = parse("vou a Lisboa amanhã")
    assert r is not None
    s, remainder = r
    assert "vou a Lisboa" in remainder
