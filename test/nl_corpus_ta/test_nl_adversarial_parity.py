# -*- coding: utf-8 -*-
"""Adversarial Tamil cases plus the shared English semantic-parity block."""
import pytest

from ._corpus import nomatch, parse


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["நாள்", "வாரம்", "மாதம்", "ஆண்டு",
                                  "மணிநேரம்", "நிமிடம்", "விநாடி"])
def test_a_bare_unit_without_a_count_is_not_an_offset(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["முன்", "பிறகு", "ஒவ்வொரு", "இல்"])
def test_a_lone_marker_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["கடந்த", "இந்த", "அடுத்த"])
def test_a_lone_relative_word_is_not_a_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["ஒன்று", "இருபத்தொன்று", "பதினைந்து",
                                  "நூற்றொன்று", "ஐம்பது"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time."""
    nomatch(text)


@pytest.mark.parametrize("text", ["மணி", "கால்", "அரை", "முக்கால்"])
def test_a_bare_clock_word_is_not_a_time(text):
    """மணி is "bell" first and கால் is "leg"; both are read as clock words
    only beside a numeral, and never bind a slot on their own."""
    nomatch(text)


@pytest.mark.parametrize("text", ["இரண்டு திங்கள்", "ஐந்து திங்கள்"])
def test_a_counted_monday_refuses(text):
    """திங்கள் is Monday and also the month, so a count in front of it can
    only be the duration this locale does not express with that word."""
    nomatch(text)


PAIRS = [
    ("இன்று", "today"),
    ("நாளை", "tomorrow"),
    ("நேற்று", "yesterday"),
    ("நேற்று முன்தினம்", "the day before yesterday"),
    ("நாளை மறுநாள்", "overmorrow"),
    ("மூன்று நாட்களுக்கு முன்", "3 days ago"),
    ("ஐந்து நாட்களுக்கு முன்", "5 days ago"),
    ("இருபத்தொன்று நாட்களுக்கு முன்", "21 days ago"),
    ("இரண்டு மணிநேரம் முன்", "2 hours ago"),
    ("பத்து நிமிடங்களுக்கு முன்", "10 minutes ago"),
    ("பதினைந்து நிமிடங்களுக்கு முன்", "15 minutes ago"),
    ("முப்பது விநாடிகளுக்கு முன்", "30 seconds ago"),
    ("இரண்டு வாரங்களுக்கு முன்", "2 weeks ago"),
    ("மூன்று மாதங்களுக்கு முன்", "3 months ago"),
    ("இரண்டு ஆண்டுகளுக்கு முன்", "2 years ago"),
    ("பதினொன்று ஆண்டுகளுக்கு முன்", "11 years ago"),
    ("நூறு ஆண்டுகளுக்கு முன்", "100 years ago"),
    ("இரண்டு நாட்களில்", "in 2 days"),
    ("மூன்று மணிநேரத்தில்", "in 3 hours"),
    ("இருபது நிமிடங்களில்", "in 20 minutes"),
    ("ஒரு வாரத்தில்", "in 1 week"),
    ("ஆறு மாதங்களில்", "in 6 months"),
    ("இந்த ஆண்டு", "this year"),
    ("கடந்த ஆண்டு", "last year"),
    ("அடுத்த ஆண்டு", "next year"),
    ("இந்த மாதம்", "this month"),
    ("கடந்த மாதம்", "last month"),
    ("அடுத்த மாதம்", "next month"),
    ("இந்த வாரம்", "this week"),
    ("கடந்த வாரம்", "last week"),
    ("அடுத்த வாரம்", "next week"),
    ("அடுத்த திங்கள்", "next monday"),
    ("கடந்த வெள்ளி", "last friday"),
    ("அடுத்த ஞாயிறு", "next sunday"),
    ("15 ஜனவரி 2026", "15 january 2026"),
    ("ஜனவரி 2026", "january 2026"),
    ("15 மார்ச்", "15 march"),
    ("டிசம்பர்", "december"),
    ("இரண்டு ஆயிரம் இருபது", "2020"),
    ("நண்பகல்", "noon"),
    ("ஒன்பதரை மணி", "9:30"),
    ("ஒன்பதே கால்", "9:15"),
    ("மாலை ஆறு மணி", "6 pm"),
    ("காலை எட்டு மணி", "8 am"),
    ("இரவு இரண்டு மணி", "2 am"),
    ("மூன்று மணிக்கு பத்து நிமிடம் மேல்", "3:10"),
    ("ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு", "5:45"),
]
