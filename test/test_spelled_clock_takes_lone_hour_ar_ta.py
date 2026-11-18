# -*- coding: utf-8 -*-
"""A spelled ar or ta clock reads like its digit twin.

Speech recognition writes a spoken "three thirty" as "3:30", so the two forms
read alike (ruling 23): with no part of the day the hour takes whichever of its
two twelve-hour readings comes next after the anchor.  The ar and ta folds
write a clock from spelled words, and that clock took the written hour while
the digit twin took the next reading.

Anchor: Tuesday 2017-06-27 13:04.  Every expected instant is the next 6:30,
9:30, 9:15, 3:10 or 5:45 after 13:04, worked out by hand: 6:30 is 18:30 the
same day, 9:30 is 21:30, 9:15 is 21:15, 3:10 is 15:10 and 5:45 is 17:45.  A
part of the day keeps the written half of the day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
TODAY = datetime(2017, 6, 27)
TOMORROW = datetime(2017, 6, 28)

# spelled text, digit twin, language, expected instant
TWINS = [
    ("الساعة السادسة والنصف", "الساعة 6:30", "ar", TODAY.replace(hour=18, minute=30)),
    ("ஒன்பதரை மணி", "9:30", "ta", TODAY.replace(hour=21, minute=30)),
    ("ஒன்பதே கால்", "9:15", "ta", TODAY.replace(hour=21, minute=15)),
    ("மூன்று மணிக்கு பத்து நிமிடம் மேல்", "3:10", "ta",
     TODAY.replace(hour=15, minute=10)),
    ("ஆறு மணிக்கு பதினைந்து நிமிடம் குறைவு", "5:45", "ta",
     TODAY.replace(hour=17, minute=45)),
]


@pytest.mark.parametrize("spelled,digits,lang,instant", TWINS)
def test_spelled_clock_and_digit_twin_agree(spelled, digits, lang, instant):
    for text in (spelled, digits):
        found = extract_timespan(text, lang, ANCHOR)
        assert found.span.start.datetime() == instant, text
        assert found.remainder == "", text


@pytest.mark.parametrize("text,lang,instant", [
    ("الساعة السادسة والنصف صباحا", "ar", TOMORROW.replace(hour=6, minute=30)),
    ("غدا الساعة السادسة والنصف", "ar", TOMORROW.replace(hour=6, minute=30)),
    ("الساعة الثانية عشرة والنصف", "ar", TOMORROW.replace(hour=12, minute=30)),
])
def test_part_of_day_day_word_and_twelve_keep_the_written_hour(text, lang,
                                                              instant):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == instant
