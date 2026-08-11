# -*- coding: utf-8 -*-
"""Regression for defect R124: the two-word "a las" preposition before a
bare digital clock ("a las 15:00") is stranded as unconsumed remainder on
the ``extract_timespan`` path.

es's ``clock_time`` grammar's bare-CLOCK order ("CLOCK MERIDIEM? ZONE?")
has no leading ``at?`` slot, unlike the HOUR-based orders in the same
construction.  ``marker_at.voc`` for es already contains both "a" and
"las" as separate marker tokens (each combined article word), so an
``at?`` slot at the head of the CLOCK order consumes the whole two-word
phrase.  The fix adds a mirrored ``at? CLOCK MERIDIEM? ZONE?`` order.

Anchor is the shared es corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse


def test_two_word_at_marker_consumed():
    r = parse("a las 15:00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert remainder == ""


def test_embedded_in_sentence():
    r = parse("la reunión es a las 15:00 en la oficina")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "a las" not in remainder


def test_generic_preposition_a_survives():
    # "a" as a plain preposition ("to") before a place must not be eaten.
    r = parse("voy a Madrid mañana")
    assert r is not None
    s, remainder = r
    assert "voy a Madrid" in remainder
