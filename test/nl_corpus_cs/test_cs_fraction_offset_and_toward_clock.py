"""Czech fractional-unit offsets and the toward-hour quarter.

Two constructions, both first-week utterances:

* the fractional offset -- "za pul hodiny" is "in half an hour", the
  quantifier 0.5 bound to the unit noun, exactly as "za pet minut" binds a
  cardinal to it.  Citation: Internetova jazykova prirucka (Ustav pro jazyk
  cesky AV CR), s.v. "pul", the half of a unit before a genitive noun.
* the toward-hour quarter -- "ctvrt na devet" is a quarter ONTO the ninth
  hour, 08:15, and "trictvrte na devet" is three quarters onto it, 08:45.
  The connector is "na" (onto), not the subtractive "do"/"pred", so the
  named hour is the COMING one and the minutes count forward from the hour
  before it.  Citation: Internetova jazykova prirucka (UJC AV CR),
  "Vyjadrovani casu", worked examples "ctvrt na sedm" == 6.15 and
  "tri ctvrte na sedm" == 6.45.

Exact values, hand-derived from the anchor; no reading comes from the parser.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start, nomatch


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


def _clean(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r[1] == "", f"{text!r} stranded {r[1]!r}"
    return r[0].start


@pytest.mark.parametrize("text,minutes", [
    ("za půl hodiny", 30),
    ("za čtvrt hodiny", 15),
    ("za půldruhé hodiny", 90),
])
def test_fractional_unit_offset(text, minutes):
    assert _clean(text) == ad(ANCHOR + timedelta(minutes=minutes))


def test_fractional_offset_is_not_a_whole_unit():
    # Adversarial pin: "za pul hodiny" must NOT be read as the bare unit
    # offset "za hodinu" (+60 minutes) with the quantifier dropped.
    assert _clean("za půl hodiny") == ad(ANCHOR + timedelta(minutes=30))
    assert _clean("za hodinu") == ad(ANCHOR + timedelta(minutes=60))


@pytest.mark.parametrize("text,h,mi", [
    ("čtvrt na devět", 8, 15),
    ("ve čtvrt na devět", 8, 15),
    ("třičtvrtě na devět", 8, 45),
    ("čtvrt na sedm", 6, 15),        # UJC worked example
    ("třičtvrtě na sedm", 6, 45),    # UJC worked example
    ("tři čtvrtě na sedm", 6, 45),   # the spaced spelling UJC itself writes
    ("tři čtvrtě na devět", 8, 45),
])
def test_toward_hour_quarters(text, h, mi):
    assert _clean(text) == _next_time(h, mi)


def test_toward_hour_quarter_is_before_the_named_hour_not_after():
    # Adversarial direction pin.  "ctvrt na devet" is 45 minutes BEFORE nine
    # o'clock; the reversed (subtractive/"quarter to") reading would be 08:45
    # and the past-the-named-hour reading would be 09:15.  Both wrong values
    # are literals here, never read back from the parser.
    got = _clean("čtvrt na devět")
    assert got == _next_time(8, 15)
    assert got != _next_time(8, 45)
    assert got != _next_time(9, 15)
    assert _next_time(9, 0) - got == timedelta(minutes=45)


def test_toward_hour_three_quarters_is_fifteen_minutes_before_the_hour():
    got = _clean("třičtvrtě na devět")
    assert got == _next_time(8, 45)
    assert got != _next_time(9, 45)
    assert _next_time(9, 0) - got == timedelta(minutes=15)


@pytest.mark.parametrize("text,h,mi", [
    ("čtvrt na devět ráno", 8, 15),
    ("čtvrt na devět večer", 20, 15),
])
def test_toward_hour_quarter_with_daypart(text, h, mi):
    # The day part must shift the whole reading by twelve hours, never undo
    # the fraction: the evening form is 20:15, not 20:45 or 21:15.
    assert _clean(text) == _next_time(h, mi)


def test_half_toward_hour_still_reads(): 
    # The pre-existing "pul devate" == 08:30 must be untouched by the quarter
    # wiring above.
    assert _clean("půl deváté") == _next_time(8, 30)


def test_duration_is_not_a_clock():
    nomatch("2 hodiny 30 minut")
