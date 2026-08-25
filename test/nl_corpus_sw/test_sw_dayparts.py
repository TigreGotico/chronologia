"""The five day-part bands, and why there are five rather than four.

CLDR draws Swahili's day in five stretches plus two points.  Two of them split
what English calls morning: alfajiri is the dark hours before sunrise and
asubuhi the hours after it, and collapsing the pair into one "morning" would
answer 04:00-12:00 for a word whose speakers mean 07:00-12:00.  The afternoon
closes at 16:00 and the evening at 19:00, so the night is the long band running
from 19:00 round to dawn.

The two points CLDR also lists are spelled with the sunrise-anchored clock --
"saa sita za mchana" for noon and "saa sita za usiku" for midnight -- and are
not shipped; see test_sw_refusals.
"""
import pytest

from chronologia.dayparts import lookup

from ._corpus import ad, band, nomatch, span, start_end


BANDS = [
    ("alfajiri", (4, 0), (7, 0), 0),
    ("asubuhi", (7, 0), (12, 0), 0),
    ("mchana", (12, 0), (16, 0), 0),
    ("jioni", (16, 0), (19, 0), 0),
    ("usiku", (19, 0), (4, 0), 1),
]


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_each_band_resolves_to_its_cldr_hours(word, lo, hi, days):
    assert start_end(word) == band(2027, 5, 12, lo, hi, days)


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_the_registry_carries_the_band_under_the_sw_tag(word, lo, hi, days):
    dp = lookup(word, "sw")
    assert (dp.start.hour, dp.start.minute) == lo
    assert (dp.end.hour, dp.end.minute) == hi
    assert dp.crosses_midnight is bool(days)


def test_the_two_morning_bands_are_not_one():
    """alfajiri stops where asubuhi starts, and neither covers the other."""
    assert lookup("alfajiri", "sw").end == lookup("asubuhi", "sw").start
    assert lookup("alfajiri", "sw").start.hour == 4
    assert lookup("asubuhi", "sw").start.hour == 7


def test_the_night_wraps_past_midnight():
    s = span("usiku")
    assert s.start.hour == 19 and s.end.hour == 4
    assert s.end.day == s.start.day + 1


def test_the_afternoon_closes_before_the_english_one():
    """mchana ends at 16:00; the English afternoon runs to 18:00."""
    assert lookup("mchana", "sw").end.hour == 16
    assert lookup("jioni", "sw").start.hour == 16


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_a_band_anchors_onto_a_named_day(word, lo, hi, days):
    assert start_end(f"kesho {word}") == band(2027, 5, 13, lo, hi, days)


@pytest.mark.parametrize("text", [
    "machweo", "adhuhuri", "magharibi", "mapambazuko",
])
def test_no_sixth_band_is_invented(text):
    """CLDR draws five bands.  Other words for stretches of the day get none."""
    nomatch(text)


def test_a_qualifier_on_a_band_narrows_nothing():
    """"usiku wa manane" is the dead of night, and gets the whole night.

    usiku alone IS a band, so the phrase resolves -- but only to the band its
    first word names.  The qualifier stays in the remainder rather than being
    given boundaries no source states.
    """
    from ._corpus import remainder
    s = span("usiku wa manane")
    assert (s.start.hour, s.end.hour) == (19, 4)
    assert remainder("usiku wa manane") != ""


# -- the counted-hour veto must not cost the bands themselves ---------------
# A counted saa beside a band vetoes the band (test_sw_clock), because the
# phrase names an hour this locale refuses to read.  Everything that names no
# hour must be untouched by that veto.

@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_a_bare_band_survives_the_counted_hour_veto(word, lo, hi, days):
    assert start_end(word) == band(2027, 5, 12, lo, hi, days)


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_a_band_on_a_named_day_survives_the_veto(word, lo, hi, days):
    """"kesho usiku" carries a count-shaped word before the band and must live."""
    assert start_end(f"jana {word}") == band(2027, 5, 11, lo, hi, days)


@pytest.mark.parametrize("word,lo,hi,days", BANDS)
def test_an_uncounted_saa_does_not_veto_a_band(word, lo, hi, days):
    """The veto needs a COUNT: a bare saa with no numeral is not a named hour."""
    r = span(f"saa {word}")
    assert (r.start.hour, r.end.hour) == (lo[0], hi[0])
