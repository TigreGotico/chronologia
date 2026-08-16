# -*- coding: utf-8 -*-
"""R187: the Dutch mirror of the English "tonight at 8" fix.

"vanavond" ("this evening"), "vanochtend"/"vanmorgen" ("this morning") are
single-word today+daypart surfaces (the ANW carries all three as their own
dictionary entries) composed with a preceding "om <hour> uur" clock.  Before
this fix "vanavond om 8 uur" (anchor 10:00) rolled to tomorrow 20:00, for the
same reason as the English "tonight at 8": the clock's own resolution rolled
the UNSHIFTED hour 8 forward (8 < 10) before the day-part's PM shift ran.

"vanmorgen" was additionally missing from the day-part vocabulary entirely
(only "vanochtend" was recognised), so "vanmorgen om 8 uur" stranded
"vanmorgen" in the remainder on top of the roll bug -- both are fixed
together here since they land on the same composition path once the surface
is recognised.

A genuinely bare, non-explicit day-part ("avond om 3 uur", no "van-" prefix)
keeps the clock's own roll-to-tomorrow rule, unaffected by this fix.

Anchor: Friday 2026-08-14 10:00.

Gold is derived by hand: today's date at the PM-shifted hour for the PM-side
"vanavond", the literal hour for the AM-side "vanochtend"/"vanmorgen".
"""
import pytest

from ._corpus import parse

ANCHOR_R187 = __import__("datetime").datetime(2026, 8, 14, 10, 0)
TODAY = 14


def _p(text):
    return parse(text, ANCHOR_R187)


def _pm(h):
    return h + 12 if h != 12 else 12


def _am(h):
    return h if h != 12 else 12


@pytest.mark.parametrize("h", range(1, 13))
def test_vanavond_stays_on_anchor_day(h):
    text = f"vanavond om {h} uur"
    r = _p(text)
    assert r is not None, f"{text!r} did not parse"
    s = r.span.start
    assert (s.year, s.month, s.day) == (2026, 8, TODAY), text
    assert s.hour == _pm(h), text
    assert r.remainder == "", text


@pytest.mark.parametrize("daypart", ["vanochtend", "vanmorgen"])
@pytest.mark.parametrize("h", range(1, 13))
def test_vanochtend_and_vanmorgen_stay_on_anchor_day(daypart, h):
    text = f"{daypart} om {h} uur"
    r = _p(text)
    assert r is not None, f"{text!r} did not parse"
    s = r.span.start
    assert (s.year, s.month, s.day) == (2026, 8, TODAY), text
    assert s.hour == _am(h), text
    assert r.remainder == "", text


def test_bare_non_explicit_daypart_still_rolls_forward():
    """"avond om 3 uur" (no "van-" prefix) keeps the clock's own
    roll-to-tomorrow rule, untouched by this fix."""
    r = _p("avond om 3 uur")
    assert r is not None
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour) == (2026, 8, 15, 15)


def test_bare_vanavond_band_still_todays_evening():
    """A bare "vanavond" with no clock stays the whole-band reading."""
    r = _p("vanavond")
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour) == (2026, 8, TODAY, 18)
