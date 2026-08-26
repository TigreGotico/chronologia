# -*- coding: utf-8 -*-
"""The nine day-period bands, and how one of them picks the hour.

CLDR draws nine bands for Tamil, at the high end of what it carries for any
locale, and the extra cuts are real: அதிகாலை is the pre-dawn stretch and not a
synonym for காலை, and மாலை and அந்தி மாலை split the evening at 18:00.  A
day-period word in front of a clock phrase is what says which half of the day
the hour belongs to, and the band it names is what decides -- not a blanket
"add twelve", which would read இரவு இரண்டு மணி as 14:00 instead of 02:00.
"""
import pytest

from ._corpus import band, minute_at, nomatch, start_end


@pytest.mark.parametrize("text,expected", [
    ("அதிகாலை", band(2027, 5, 12, (3, 0), (5, 0))),
    ("காலை", band(2027, 5, 12, (5, 0), (12, 0))),
    ("மதியம்", band(2027, 5, 12, (12, 0), (14, 0))),
    ("பிற்பகல்", band(2027, 5, 12, (14, 0), (16, 0))),
    ("மாலை", band(2027, 5, 12, (16, 0), (18, 0))),
    ("அந்தி மாலை", band(2027, 5, 12, (18, 0), (21, 0))),
    ("இரவு", band(2027, 5, 12, (21, 0), (3, 0), days=1)),
])
def test_each_band_is_its_own_stretch_of_the_day(text, expected):
    assert start_end(text) == expected


def test_the_pre_dawn_band_is_not_the_morning():
    """அதிகாலை opens at 03:00 and closes where காலை opens; collapsing the two
    would answer nine hours for a word that names two."""
    assert start_end("அதிகாலை") != start_end("காலை")


def test_the_two_evening_bands_are_not_one():
    assert start_end("மாலை") != start_end("அந்தி மாலை")


@pytest.mark.parametrize("text,expected", [
    ("காலை எட்டு மணி", minute_at(2027, 5, 13, 8, 0)),
    ("காலை ஒன்பதரை மணி", minute_at(2027, 5, 13, 9, 30)),
    ("மதியம் ஒரு மணி", minute_at(2027, 5, 13, 13, 0)),
    ("பிற்பகல் மூன்று மணி", minute_at(2027, 5, 12, 15, 0)),
    ("மாலை ஆறு மணி", minute_at(2027, 5, 12, 18, 0)),
    ("அந்தி மாலை ஏழு மணி", minute_at(2027, 5, 12, 19, 0)),
    ("அதிகாலை நான்கு மணி", minute_at(2027, 5, 13, 4, 0)),
])
def test_the_band_picks_the_half_day(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    # இரவு wraps midnight, which is exactly where a flat +12 goes wrong.
    ("இரவு ஒன்பது மணி", minute_at(2027, 5, 12, 21, 0)),
    ("இரவு இரண்டு மணி", minute_at(2027, 5, 13, 2, 0)),
    ("இரவு பன்னிரண்டு மணி", minute_at(2027, 5, 13, 0, 0)),
])
def test_the_midnight_crossing_band_is_not_a_flat_twelve_hour_shift(
        text, expected):
    assert start_end(text) == expected


def test_two_in_the_small_hours_is_not_two_in_the_afternoon():
    assert start_end("இரவு இரண்டு மணி")[0].hour == 2


@pytest.mark.parametrize("text", [
    "காலை ஒரு மணி",
    "மதியம் எட்டு மணி",
    "அதிகாலை பத்து மணி",
])
def test_an_hour_outside_the_named_band_refuses(text):
    """Neither twelve-hour reading of the hour falls inside the band, so
    nothing in the phrase chooses one and the extractor answers nothing."""
    nomatch(text)


def test_noon_is_a_landmark_not_a_band():
    """நண்பகல் falls on the மதியம் boundary and draws no stretch of its own,
    so it names the single minute rather than the band behind it."""
    assert start_end("நண்பகல்") == minute_at(2027, 5, 13, 12, 0)
