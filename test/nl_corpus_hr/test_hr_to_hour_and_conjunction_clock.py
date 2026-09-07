"""Croatian subtractive clock and the "hour AND minutes" conjunction.

Two constructions Croatian speakers use every day and the engine could not
read:

* the subtractive form -- "petnaest do devet" is fifteen minutes TO nine,
  08:45, and "cetvrt do devet" the same quantity named as a quarter.  "do"
  is the ordinary "to/until" preposition, so the minutes are SUBTRACTED
  from the named hour.  This is the opposite direction to "pola devet"
  (half toward nine == 08:30), which takes no direction word at all.
  Citations: en.wiktionary.org/wiki/do#Serbo-Croatian ("to, until, up to");
  hjp.znanje.hr, s.v. "cetvrt", with the clock example "cetvrt do devet".
* the conjunction form -- "osam i petnaest" is eight and fifteen, 08:15.
  This is what ``nice_time_hr`` speaks, so it is also the TTS round trip.

The conjunction form previously answered the bare hour and left "i petnaest"
stranded -- a wrong time rather than a refusal, which is why every case here
asserts the exact value AND an empty remainder.
"""
from datetime import timedelta

import pytest

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
    ("četvrt do devet", 8, 45),
    ("petnaest do devet", 8, 45),
    ("deset do devet", 8, 50),
    ("pet do tri", 2, 55),
])
def test_minutes_and_quarter_to_the_hour(text, h, mi):
    assert _clean(text) == _next_time(h, mi)


def test_to_the_hour_is_before_the_named_hour_not_after():
    # Adversarial direction pin: "petnaest do devet" is 15 minutes BEFORE
    # nine o'clock.  The reversed reading would be 09:15 and the toward-hour
    # reading (the one "pola" takes) would be 08:15 -- both written here as
    # literals, never read back from the parser.
    got = _clean("petnaest do devet")
    assert got == _next_time(8, 45)
    assert got != _next_time(9, 15)
    assert got != _next_time(8, 15)
    assert _next_time(9, 0) - got == timedelta(minutes=15)


@pytest.mark.parametrize("text,h,mi", [
    ("u osam i petnaest", 8, 15),
    ("osam i petnaest", 8, 15),
    ("osam i trideset", 8, 30),
    ("u dva i trideset", 2, 30),
])
def test_hour_and_minutes(text, h, mi):
    assert _clean(text) == _next_time(h, mi)


def test_hour_and_minutes_is_after_the_named_hour():
    # "osam i petnaest" is 15 minutes PAST eight.  The subtractive reading
    # would be 07:45 and the bare hour (the old stranded answer) 08:00.
    got = _clean("u osam i petnaest")
    assert got == _next_time(8, 15)
    assert got != _next_time(7, 45)
    assert got != _next_time(8, 0)
    assert got - _next_time(8, 0) == timedelta(minutes=15)


@pytest.mark.parametrize("text,h,mi", [
    ("petnaest do devet navečer", 20, 45),
    ("u osam i petnaest navečer", 20, 15),
])
def test_daypart_shifts_the_hour_not_the_minutes(text, h, mi):
    # The evening day part moves the reading twelve hours, never re-signs the
    # minute offset: "petnaest do devet navecer" is 20:45, not 21:15 or
    # 20:15; "u osam i petnaest navecer" is 20:15, not 20:45.
    assert _clean(text) == _next_time(h, mi)


def test_evening_form_is_the_same_minutes_twelve_hours_apart():
    # Both readings name :45, differing only in the hour -- a day part that
    # re-signed the offset would give 20:15 or 21:15 for the evening form.
    assert _clean("petnaest do devet").minute == 45
    assert _clean("petnaest do devet navečer").minute == 45
    assert _clean("petnaest do devet").hour == 8
    assert _clean("petnaest do devet navečer").hour == 20


def test_bare_quarter_without_a_direction_word_is_not_a_clock():
    # Croatian never says a bare "cetvrt devet" for 08:15 -- only "pola"
    # takes the bare toward-hour form -- so it stays unparsed rather than
    # being guessed.
    nomatch("četvrt devet")


def test_half_toward_hour_still_reads():
    assert _clean("pola devet") == _next_time(8, 30)


def test_duration_is_not_a_clock():
    nomatch("2 sata i 30 minuta")
