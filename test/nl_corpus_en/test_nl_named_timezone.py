"""RFC/ISO numeric offsets and common fixed-offset zone abbreviations.

A trailing signed numeric offset ("-0500", "+05:30") or a common, unambiguous
zone abbreviation ("EST", "CET") makes a clock span **aware** -- its ``tzinfo``
carries a *fixed* offset -- without changing the wall-clock digits.  "3pm EST"
is 15:00 tagged UTC-5, NOT converted to 20:00 UTC.

These abbreviations are mapped as **fixed** offsets, a deliberate
simplification: they are NOT DST-aware IANA zones.  Genuinely ambiguous
abbreviations (IST, ACST, CST-as-China, ...) and city/region words
("Eastern time", "New York time") are out of scope and must NOT fabricate an
offset -- they stay naive with the word left in the remainder.

Anchor: Tuesday 2017-06-27 13:04 (prefer_future applies to the naive wall time).
"""
from datetime import timedelta, timezone

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import ANCHOR, span, parse


def _aw(y, mo, d, h, mi, off_minutes):
    return AstroDate(y, mo, d, h, mi, tzinfo=timezone(timedelta(minutes=off_minutes)))


# -- RFC / ISO signed numeric offsets ---------------------------------------
_NUMERIC = [
    ("8am -0500", _aw(2017, 6, 28, 8, 0, -300)),    # 08:00 < 13:04 -> tomorrow
    ("3pm -0500", _aw(2017, 6, 27, 15, 0, -300)),
    ("9:30 +05:30", _aw(2017, 6, 28, 9, 30, 330)),
    ("3pm +0530", _aw(2017, 6, 27, 15, 0, 330)),
    ("3pm -08:00", _aw(2017, 6, 27, 15, 0, -480)),
    ("11pm +0100", _aw(2017, 6, 27, 23, 0, 60)),
]


@pytest.mark.parametrize("text,want", _NUMERIC)
def test_numeric_offset(text, want):
    s = span(text).start
    assert s.tzinfo is not None, f"{text!r} produced a naive time"
    assert s.utcoffset() == want.utcoffset()
    # wall-clock digits are unchanged (NOT converted to UTC)
    assert (s.year, s.month, s.day, s.hour, s.minute) == \
        (want.year, want.month, want.day, want.hour, want.minute)


# -- curated fixed-offset abbreviations --------------------------------------
_NAMED = [
    ("3pm EST", -300), ("3pm EDT", -240),
    ("3pm PST", -480), ("3pm PDT", -420),
    ("3pm MST", -420), ("3pm MDT", -360),
    ("3pm CDT", -300),               # US Central Daylight
    ("3pm CET", 60), ("3pm CEST", 120),
    ("3pm EET", 120), ("3pm WET", 0),
    ("3pm BST", 60),                 # British Summer Time
    ("3pm JST", 540), ("3pm KST", 540),
    ("3pm AEST", 600), ("3pm AEDT", 660),
    ("3pm NZST", 720),
]


@pytest.mark.parametrize("text,off", _NAMED)
def test_named_abbrev(text, off):
    s = span(text).start
    assert s.tzinfo is not None, f"{text!r} produced a naive time"
    assert s.utcoffset() == timedelta(minutes=off)
    # 3pm stays 15:00 on the anchor day, tagged not converted
    assert (s.year, s.month, s.day, s.hour, s.minute) == (2017, 6, 27, 15, 0)


def test_us_central_cst():
    s = span("3pm CST").start
    assert s.utcoffset() == timedelta(minutes=-360)  # US Central Standard


# -- regression pins: nothing that worked before changes ---------------------
def test_bare_clock_stays_naive():
    assert span("3pm").start.tzinfo is None
    assert span("8am").start.tzinfo is None


def test_utc_gmt_numeric_unchanged():
    assert span("noon UTC+2").start.utcoffset() == timedelta(minutes=120)
    assert span("midnight GMT").start.utcoffset() == timedelta(0)
    assert span("5pm GMT+1").start.utcoffset() == timedelta(minutes=60)
    assert span("14:00 UTC").start.utcoffset() == timedelta(0)


# -- deferred ambiguous abbreviations must NOT fabricate an offset ------------
# IST (India +5:30 / Israel +2 / Irish +1), city/region words -> stay naive,
# the token is left in the remainder rather than guessing a zone.
@pytest.mark.parametrize("text,leftover", [
    ("3pm IST", "ist"),
    ("3pm Eastern", "eastern"),
    ("3pm Berlin", "berlin"),
])
def test_ambiguous_stays_naive(text, leftover):
    r = parse(text)
    assert r is not None
    assert r[0].start.tzinfo is None, f"{text!r} fabricated a zone"
    assert leftover in r[1].lower()
