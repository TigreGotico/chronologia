# -*- coding: utf-8 -*-
"""Offsets and the relative period words.

Tamil marks the direction of an offset on the counted noun itself.  "Ago" is
the DATIVE unit plus a trailing முன்; "in N units" is the LOCATIVE unit and
nothing else, which is why the two directions differ by a suffix rather than by
a word.  Every expectation below is computed from the anchor by
:mod:`datetime` arithmetic, never read back from the parser.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, day, nomatch, start, start_end


@pytest.mark.parametrize("text,days", [
    ("ஒரு நாளுக்கு முன்", 1),
    ("மூன்று நாட்களுக்கு முன்", 3),
    ("ஐந்து நாட்களுக்கு முன்", 5),
    ("பத்து நாட்களுக்கு முன்", 10),
    ("இருபத்தொன்று நாட்களுக்கு முன்", 21),
])
def test_the_dative_plus_mun_is_the_past(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))


@pytest.mark.parametrize("text,days", [
    ("ஒரு நாளில்", 1),
    ("இரண்டு நாட்களில்", 2),
    ("ஏழு நாட்களில்", 7),
    ("முப்பது நாட்களில்", 30),
])
def test_the_locative_alone_is_the_future(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


def test_the_two_directions_of_one_count_are_not_the_same_day():
    """The suffix is the only thing separating them, so a fold that dropped it
    would make both readings the same and neither would be visibly wrong."""
    assert start("மூன்று நாட்களுக்கு முன்") != start("மூன்று நாட்களில்")


@pytest.mark.parametrize("text,delta", [
    ("இரண்டு மணிநேரம் முன்", timedelta(hours=-2)),
    ("மூன்று மணிநேரத்தில்", timedelta(hours=3)),
    ("பத்து நிமிடங்களுக்கு முன்", timedelta(minutes=-10)),
    ("பதினைந்து நிமிடங்களுக்கு முன்", timedelta(minutes=-15)),
    ("இருபது நிமிடங்களில்", timedelta(minutes=20)),
    ("முப்பது விநாடிகளுக்கு முன்", timedelta(seconds=-30)),
    ("ஐம்பது விநாடிகளில்", timedelta(seconds=50)),
])
def test_the_sub_day_units(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,weeks", [
    ("ஒரு வாரத்திற்கு முன்", -1),
    ("இரண்டு வாரங்களுக்கு முன்", -2),
    ("ஒரு வாரத்தில்", 1),
    ("மூன்று வாரங்களில்", 3),
])
def test_the_week_offsets(text, weeks):
    assert start(text) == ad(ANCHOR + timedelta(weeks=weeks))


@pytest.mark.parametrize("text,expected", [
    # the anchor is 2027-05-12, so the month and year arithmetic is exact.
    ("மூன்று மாதங்களுக்கு முன்", (2027, 2, 12)),
    ("ஆறு மாதங்களில்", (2027, 11, 12)),
    ("இரண்டு ஆண்டுகளுக்கு முன்", (2025, 5, 12)),
    ("பதினொன்று ஆண்டுகளுக்கு முன்", (2016, 5, 12)),
    ("நூறு ஆண்டுகளுக்கு முன்", (1927, 5, 12)),
    ("ஐந்து ஆண்டுகளில்", (2032, 5, 12)),
])
def test_the_month_and_year_offsets(text, expected):
    got = start(text)
    assert (got.year, got.month, got.day) == expected


@pytest.mark.parametrize("text,expected", [
    ("இன்று", day(2027, 5, 12)),
    ("நாளை", day(2027, 5, 13)),
    ("நேற்று", day(2027, 5, 11)),
    ("நேற்று முன்தினம்", day(2027, 5, 10)),
    ("நாளை மறுநாள்", day(2027, 5, 14)),
])
def test_the_deictic_days(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("இந்த ஆண்டு", (2027, 1, 1)),
    ("கடந்த ஆண்டு", (2026, 1, 1)),
    ("அடுத்த ஆண்டு", (2028, 1, 1)),
    ("இந்த மாதம்", (2027, 5, 1)),
    ("கடந்த மாதம்", (2027, 4, 1)),
    ("அடுத்த மாதம்", (2027, 6, 1)),
])
def test_the_relative_periods(text, expected):
    got = start(text)
    assert (got.year, got.month, got.day) == expected


@pytest.mark.parametrize("text,expected", [
    # the anchor is a Wednesday, so the week that contains it opens Monday
    # the 10th; the neighbouring weeks are seven days out either way.
    ("இந்த வாரம்", (2027, 5, 10)),
    ("கடந்த வாரம்", (2027, 5, 3)),
    ("அடுத்த வாரம்", (2027, 5, 17)),
])
def test_the_relative_weeks(text, expected):
    got = start(text)
    assert (got.year, got.month, got.day) == expected


@pytest.mark.parametrize("text,expected", [
    # Wednesday the 12th is the anchor: Friday is two days on, the previous
    # Friday two days before the week opened, and Sunday closes this week.
    ("அடுத்த வெள்ளி", day(2027, 5, 14)),
    ("கடந்த வெள்ளி", day(2027, 5, 7)),
    ("அடுத்த ஞாயிறு", day(2027, 5, 16)),
    ("அடுத்த செவ்வாய்", day(2027, 5, 18)),
    ("கடந்த புதன்", day(2027, 5, 5)),
])
def test_the_relative_weekdays(text, expected):
    assert start_end(text) == expected


@pytest.mark.parametrize("text", ["முன்", "இல்", "கடந்த", "அடுத்த", "இந்த",
                                  "ஒவ்வொரு", "பிறகு"])
def test_a_lone_marker_names_no_time(text):
    nomatch(text)
