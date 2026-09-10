"""Slovak toward-hour clock: the half, the quarter and the three quarters.

Slovak tells the first half of an hour by naming the hour it is coming UP
TO, not the one just past:

* "pol deviatej" -- half OF THE NINTH == 08:30.  The half takes no
  connector and the hour is a genitive-feminine ordinal agreeing with the
  elided "hodiny".  Citation: Slovnik sucasneho slovenskeho jazyka
  (Jazykovedny ustav L. Stura SAV, slovnik.juls.savba.sk), s.v. "pol":
  "pol siedmej" == 6.30 h.
* "stvrt na devat" -- a quarter ONTO the ninth == 08:15, and
  "tristvrte na devat" -- three quarters onto it == 08:45.  Here the hour
  is a bare cardinal after the toward connector "na".  Citation: the same
  dictionary, s.v. "stvrt": "stvrt na osem" == 7.15 h, and s.v.
  "tristvrte": "tristvrte na osem" == 7.45 h.

Getting the direction wrong makes every one of these an hour late in
silence, so each value is pinned against its reversed reading as a literal.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

from ._corpus import ANCHOR, ad, parse, nomatch


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


@pytest.mark.parametrize("text,h,mi", [
    ("pol deviatej", 8, 30),
    ("o pol deviatej", 8, 30),
    ("o pol tretej", 2, 30),
    ("pol siedmej", 6, 30),          # JULS worked example
    ("štvrť na deväť", 8, 15),
    ("o štvrť na deväť", 8, 15),
    ("štvrť na osem", 7, 15),        # JULS worked example
    ("trištvrte na deväť", 8, 45),
    ("o trištvrte na deväť", 8, 45),
    ("trištvrte na osem", 7, 45),    # JULS worked example
])
def test_toward_hour_readings(text, h, mi):
    assert _clean(text) == _next_time(h, mi)


def test_half_names_the_coming_hour_not_the_past_one():
    # Adversarial direction pin.  "pol deviatej" is 30 minutes BEFORE nine
    # o'clock; the reversed "half past nine" reading would be 09:30.  Both
    # values are literals, never read back from the parser.
    got = _clean("pol deviatej")
    assert got == _next_time(8, 30)
    assert got != _next_time(9, 30)
    assert _next_time(9, 0) - got == timedelta(minutes=30)
    assert _clean("o deviatej") == _next_time(9, 0)


def test_quarter_onto_the_hour_is_forty_five_minutes_before_it():
    got = _clean("štvrť na deväť")
    assert got == _next_time(8, 15)
    assert got != _next_time(9, 15)     # past-the-named-hour reading
    assert got != _next_time(8, 45)     # subtractive "quarter to" reading
    assert _next_time(9, 0) - got == timedelta(minutes=45)


def test_three_quarters_onto_the_hour_is_fifteen_minutes_before_it():
    got = _clean("trištvrte na deväť")
    assert got == _next_time(8, 45)
    assert got != _next_time(9, 45)
    assert _next_time(9, 0) - got == timedelta(minutes=15)


def test_toward_the_first_hour_is_spoken_as_twelve():
    # toward_hour_12h: the hour before one is spoken as twelve, so half
    # toward one is 12:30, never 00:30.
    assert _clean("pol jednej") == _next_time(12, 30)


@pytest.mark.parametrize("text,h,mi", [
    ("o pol deviatej ráno", 8, 30),
    ("o pol deviatej večer", 20, 30),
    ("štvrť na deväť ráno", 8, 15),
    ("štvrť na deväť večer", 20, 15),
])
def test_daypart_shifts_the_hour_not_the_fraction(text, h, mi):
    # The day part moves the reading twelve hours and must not undo the
    # fraction: the evening half is 20:30, not 21:00 or 20:00.
    assert _clean(text) == _next_time(h, mi)


def test_daypart_form_is_not_the_bare_hour_with_a_stranded_fraction():
    # This phrase used to answer 09:00 with "o pol" left over -- a wrong
    # time, not a refusal.  Pin both the value and the empty remainder.
    r = parse("o pol deviatej ráno")
    assert r is not None
    assert r[1] == ""
    assert r[0].start == _next_time(8, 30)
    assert r[0].start != _next_time(9, 0)


def test_weekday_plus_toward_hour_keeps_both():
    # "v piatok o pol tretej poobede" -- Friday at half toward three in the
    # afternoon.  The next Friday after Tuesday 27 June 2017 is 30 June.
    r = parse("v piatok o pol tretej poobede")
    assert r is not None and r[1] == ""
    assert r[0].start == ad(ANCHOR.replace(day=30, hour=14, minute=30,
                                           second=0, microsecond=0))


def test_half_hour_offset_still_composes():
    # "o pol hodiny" is the OFFSET (in half an hour), not a clock reading:
    # the quantifier binds a unit noun, and freeing "pol" for the clock's
    # FRACTION slot must not break it.
    r = parse("o pol hodiny")
    assert r is not None and r[1] == ""
    assert r[0].start == ad(ANCHOR + timedelta(minutes=30))


@pytest.mark.parametrize("text,minutes", [
    ("pol hodiny", 30),
    ("pol dňa", 12 * 60),
    ("hodina a pol", 90),
    ("2 hodiny 30 minút", 150),
])
def test_durations_still_resolve_and_are_not_clocks(text, minutes):
    got = extract_duration(text, "sk")
    assert got is not None, f"{text!r} lost its duration reading"
    assert got[0] == timedelta(minutes=minutes)
    nomatch(text)
