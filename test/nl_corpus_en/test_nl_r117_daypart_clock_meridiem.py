"""R117: a day-part word PRECEDING an explicit clock composes onto it as a
meridiem hint -- it must not be dropped, and it must not lose the meridiem
tug-of-war to the bare clock reading it precedes.

Before this fix, "next tuesday evening at 9" silently read 09:00 (the
day-part span and the clock span were adjacent enough that the composer's
date+clock branch fired first, on the date and the clock alone, leaving the
day-part stranded in the remainder) -- a silent-wrong 12-hour error, not a
crash.  "next tuesday morning at 9" happened to read the *right* clock hour
by luck (morning needs no shift), but still stranded "morning" in the
remainder, which is dirty output for a clean reading.

The fix composes all three parts when adjacent: the date supplies the civil
day, the day-part supplies the AM/PM side of the bare 12-hour clock, and the
clock supplies the pinpoint minute -- so the remainder is empty and the hour
is correct in every case, including with no date at all ("afternoon at 3",
anchored to the mission anchor's own day).

Two English day-part names are exercised here: "morning" (AM-side, no
shift) and "evening"/"afternoon" (PM-side, +12 to a bare 1..11).  A
contradiction between an EXPLICIT meridiem and the day-part word --
"morning at 9pm" -- declines the whole reading (``None``), the same
refusal convention a bare contradictory hour+meridiem clock already uses
(R57): a wrong confident answer is worse than an honest miss.

Gold is derived by hand from the mission anchor
``datetime(2026, 8, 11, 12, 0)`` (a Tuesday):

* "next tuesday" is the following Tuesday, 2026-08-18 -- an explicit DATE,
  so the clock's own day-rollover rule never applies; the date's day wins
  outright.
* with no date at all, the bare pre-shift hour still goes through the
  clock's own "roll to tomorrow if already past the anchor" rule BEFORE the
  day-part's meridiem shift is applied (the two steps are independent
  passes) -- "afternoon at 3" reads the bare hour 3 first: 2026-08-11T03:00
  is before the 12:00 anchor, so it rolls to 2026-08-12T03:00, and *then*
  the day-part shifts the hour to 15:00, landing on 2026-08-12, not
  2026-08-11.  This is the pre-existing clock day-selection rule, untouched
  by this fix -- documented here, not silently assumed.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, span, start_end, nomatch

ANCHOR_R117 = __import__("datetime").datetime(2026, 8, 11, 12, 0)


def _p(text):
    return parse(text, ANCHOR_R117)


def test_preceding_evening_composes_as_pm_meridiem_on_the_clock():
    r = _p("next tuesday evening at 9")
    assert r is not None
    assert start_end("next tuesday evening at 9", ANCHOR_R117) == (
        AstroDate(2026, 8, 18, 21, 0), AstroDate(2026, 8, 18, 21, 1))
    assert r.remainder == ""


def test_preceding_morning_composes_clean_with_empty_remainder():
    r = _p("next tuesday morning at 9")
    assert r is not None
    assert start_end("next tuesday morning at 9", ANCHOR_R117) == (
        AstroDate(2026, 8, 18, 9, 0), AstroDate(2026, 8, 18, 9, 1))
    assert r.remainder == ""


def test_preceding_afternoon_shifts_a_bare_low_hour_into_the_pm_band():
    r = _p("afternoon at 3")
    assert r is not None
    # bare hour 3 rolls to the next day under the clock's own prefer-future
    # rule (2026-08-11T03:00 is before the 12:00 anchor) BEFORE the
    # day-part's meridiem shift lands it on 15:00 -- see module docstring.
    assert start_end("afternoon at 3", ANCHOR_R117) == (
        AstroDate(2026, 8, 12, 15, 0), AstroDate(2026, 8, 12, 15, 1))
    assert r.remainder == ""


def test_explicit_meridiem_contradicting_the_daypart_declines():
    """"morning at 9pm" pins the clock to 21:00 via its own explicit "pm";
    "morning" cannot agree with that -- the composer refuses rather than
    silently pick either the day-part's or the clock's reading."""
    nomatch("morning at 9pm", ANCHOR_R117)


@pytest.mark.parametrize("text,hour", [
    ("9 in the evening", 21),   # postposed English meridiem phrase
    ("9pm", 21),                # postposed literal am/pm
])
def test_postposed_meridiem_controls_are_unaffected(text, hour):
    """The postposed forms already fused the day-part/meridiem into the
    clock construction's own MERIDIEM slot before this fix landed -- they
    must keep reading correctly and unaffected by the new preposed-compose
    branch."""
    r = _p(text)
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 11, hour, 0)
    assert r.remainder == ""


def test_embedded_sentence_remainder_stays_clean_around_the_composed_reading():
    """A day-part+clock composition sitting inside a longer sentence must
    consume exactly its own tokens, leaving the surrounding words intact
    and correctly re-joined -- not stranding "evening" or "at 9" in the
    remainder alongside the unrelated words."""
    r = _p("let's meet next tuesday evening at 9 downtown")
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 18, 21, 0)
    assert r.remainder == "let's meet downtown"
