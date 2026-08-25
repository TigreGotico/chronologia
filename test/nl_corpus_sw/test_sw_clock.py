"""The clock: the digital literal reads, and "saa N" does not.

Swahili counts the hours of the day from sunrise.  Saa moja is seven in the
morning, saa sita is noon, and every reading is the Western hour minus six.
That convention is alive in written prose, not only in speech: East African
broadcasters title their own bulletins with it, publishing "Taarifa ya Habari
saa saba Mchana" for a programme that airs at 13:00 and "Taarifa ya Habari saa
2:00 Usiku" for one that airs at 20:00.

But the Western reading is alive in written Swahili too.  Fixture tables and
viewing guides for international sport, syndicated with time-zone-sensitive
digital times, use 24-hour notation and never the sunrise count.

So the same string means two things six hours apart, and which one it means is
decided by the genre the reader already knows they are in -- not by anything
present in the phrase.  A parser handed the phrase alone has no way to tell,
and every wrong guess is wrong by exactly six hours, which is the difference
between breakfast and lunch or between an evening and a small-hours
appointment.  The locale therefore reads the digital literal, which is
unambiguous, and refuses the spoken hour outright.

The refusal is narrow on purpose.  saa is also the noun for an hour of
DURATION, and CLDR's own relative-time strings are built on it -- "saa {0}
zilizopita" is N hours ago, "baada ya saa {0}" is in N hours.  Those must keep
working, so the two halves of the word are pinned side by side here.
"""
from datetime import timedelta

import pytest

from ._corpus import (ANCHOR, minute_at, nomatch, parse, remainder, span,
                      start_end)


# -- the digital clock reads -------------------------------------------------

#: (surface, hour, minute, the day it lands on).  A reading already past at
#: the 13:04 anchor rolls to the next day, as it does in every locale that
#: prefers the future.
DIGITAL = [
    ("00:00", 0, 0, 13), ("07:00", 7, 0, 13), ("09:30", 9, 30, 13),
    ("13:00", 13, 0, 13), ("14:05", 14, 5, 12), ("20:00", 20, 0, 12),
    ("21:50", 21, 50, 12), ("23:59", 23, 59, 12),
]


@pytest.mark.parametrize("text,hh,mm,dd", DIGITAL)
def test_the_digital_literal_reads(text, hh, mm, dd):
    assert start_end(text) == minute_at(2027, 5, dd, hh, mm)


def test_a_digital_time_rides_a_date():
    s = span("5 Juni 2027 14:30")
    assert (s.start.month, s.start.day, s.start.hour, s.start.minute) == (
        6, 5, 14, 30)


# -- "saa N" as a time of day does not read ---------------------------------

#: every shape the spoken hour takes, in both conventions' worth of hours.
SPOKEN_HOURS = [
    "saa moja", "saa mbili", "saa tatu", "saa nne", "saa tano", "saa sita",
    "saa saba", "saa nane", "saa tisa", "saa kumi", "saa kumi na moja",
    "saa kumi na mbili", "saa 1", "saa 3", "saa 7", "saa 12",
]


@pytest.mark.parametrize("text", SPOKEN_HOURS)
def test_a_bare_spoken_hour_names_no_time(text):
    nomatch(text)


@pytest.mark.parametrize("hour", ["moja", "mbili", "tatu", "saba", "nane",
                                  "kumi na mbili"])
@pytest.mark.parametrize("part", ["asubuhi", "mchana", "jioni", "usiku",
                                  "alfajiri"])
def test_a_spoken_hour_with_a_daypart_names_no_time(hour, part):
    """The whole phrase refuses -- the band does not answer in the hour's place.

    This is the pin the whole locale turns on, and it is about the SHAPE of the
    refusal as much as the fact of it.  "saa moja asubuhi" names one hour inside
    the morning.  Returning the 07:00-12:00 morning band with "saa moja" left in
    the remainder would hand a caller who asked for an hour a five-hour span and
    drop the part they asked about, which is a wrong answer carrying a visible
    fragment -- worse than nothing, not better.  Nor is the band a safe superset
    of the two candidate readings: the traditional saa moja asubuhi is 07:00 and
    falls inside it, while the Western one is 01:00 and does not.
    """
    nomatch(f"saa {hour} {part}")


@pytest.mark.parametrize("text", [
    "saa saba mchana", "saa mbili usiku", "saa moja asubuhi",
    "saa tatu usiku", "saa nane mchana",
    "tutakutana saa tatu usiku",
])
def test_the_attested_broadcast_titles_are_refused_a_clock(text):
    """The real published bulletin titles, and the reason for the refusal.

    "saa saba mchana" is 13:00 to KBC and 07:00 to a writer using the Western
    hour in Swahili words.  Neither is answered, and neither is the day-part
    band the phrase happens to end on.
    """
    nomatch(text)


def test_the_veto_is_declared_by_this_locale_and_no_other():
    """The ambiguous unit is a locale fact, not an engine rule.

    A locale that reads its hours normally must be untouched -- English keeps
    "at three tonight" resolving its hour deliberately -- so the veto fires
    only where a locale names the unit whose clock reading it refuses.
    """
    from chronologia.extract.loader import load_lang_spec
    key = "daypart_counted_ambiguous"
    assert load_lang_spec("sw").connectors.get(key) == frozenset({"saa"})
    for other in ("en", "mk", "id"):
        assert not load_lang_spec(other).connectors.get(key), other


@pytest.mark.parametrize("text", [
    "saa nane na robo", "saa tatu kasorobo", "saa sita na nusu",
])
def test_the_fraction_forms_of_the_spoken_clock_are_refused(text):
    """The offset applies before the fraction, so a fraction is wrong twice."""
    nomatch(text)


@pytest.mark.parametrize("text", [
    "saa sita za mchana", "saa sita za usiku",
])
def test_the_cldr_noon_and_midnight_points_are_not_landmarks(text):
    """CLDR spells both points with the sunrise count, so neither ships.

    Shipping them would put a "saa N" reading back into the locale through the
    landmark door, one hard-coded phrase at a time.  The genitive linker between
    the count and the band ("saa sita **za** mchana") does not get the band past
    the veto either.
    """
    nomatch(text)


# -- saa as a duration keeps working ----------------------------------------

@pytest.mark.parametrize("phrase,hours", [
    ("saa moja iliyopita", 1), ("saa mbili zilizopita", 2),
    ("saa tatu zilizopita", 3), ("saa sita zilizopita", 6),
    ("saa kumi na mbili zilizopita", 12), ("saa ishirini zilizopita", 20),
])
def test_saa_still_counts_hours_backwards(phrase, hours):
    assert span(phrase).start == ANCHOR - timedelta(hours=hours)


@pytest.mark.parametrize("phrase,hours", [
    ("baada ya saa moja", 1), ("baada ya saa mbili", 2),
    ("baada ya saa tatu", 3), ("baada ya saa kumi na mbili", 12),
])
def test_saa_still_counts_hours_forwards(phrase, hours):
    assert span(phrase).start == ANCHOR + timedelta(hours=hours)


def test_the_digit_form_of_the_duration_reads_too():
    assert span("saa 3 zilizopita").start == ANCHOR - timedelta(hours=3)
    assert span("baada ya saa 3").start == ANCHOR + timedelta(hours=3)


def test_the_two_readings_of_saa_are_told_apart_by_the_marker():
    """The whole split, in one place.

    With a relative marker the phrase is a duration and answers; without one it
    is a time of day and does not.  Nothing else distinguishes them, and that
    is exactly why the time of day cannot be guessed.
    """
    assert span("saa tatu zilizopita").start == ANCHOR - timedelta(hours=3)
    nomatch("saa tatu")


def test_the_hour_offset_is_not_shifted_by_six():
    """The duration reading must not pick up the sunrise offset by accident."""
    assert span("saa sita zilizopita").start == ANCHOR - timedelta(hours=6)
    assert span("baada ya saa sita").start == ANCHOR + timedelta(hours=6)


def test_no_meridiem_vocabulary_ships():
    from chronologia.extract.loader import load_lang_spec
    spec = load_lang_spec("sw")
    assert spec.meridiems == {}, "a meridiem would revive the spoken hour"
    assert spec.clock_landmarks == {}
    assert spec.clock_fractions == {}
