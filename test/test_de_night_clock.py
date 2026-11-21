# -*- coding: utf-8 -*-
"""A night word beside a twelve-hour clock picks the half that falls in the night.

Ruling 36: de "um elf Uhr nachts" is 23:00, "um drei Uhr nachts" is 03:00 and
"um zwölf Uhr nachts" is 00:00.  The night runs on both sides of midnight, so
the night word marks the reading inside the night band, 21:00 to 06:00.  When
neither half of the hour falls in the band, the clock keeps the am half.  A
24-hour clock with a night word is as written.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04: 23:00 is still ahead on the anchor day, and 03:00, 00:00 and
08:00 come on the next morning.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# text, language, expected start
NIGHT = [
    ("um elf Uhr nachts", "de", datetime(2017, 6, 27, 23, 0)),
    ("um 11 Uhr nachts", "de", datetime(2017, 6, 27, 23, 0)),
    ("um 11:00 nachts", "de", datetime(2017, 6, 27, 23, 0)),
    ("um 11:30 Uhr nachts", "de", datetime(2017, 6, 27, 23, 30)),
    ("um zehn Uhr nachts", "de", datetime(2017, 6, 27, 22, 0)),
    ("um neun Uhr nachts", "de", datetime(2017, 6, 27, 21, 0)),
    ("um drei Uhr nachts", "de", datetime(2017, 6, 28, 3, 0)),
    ("um 3:30 nachts", "de", datetime(2017, 6, 28, 3, 30)),
    ("um zwölf Uhr nachts", "de", datetime(2017, 6, 28, 0, 0)),
    # neither 08:00 nor 20:00 falls in the night band: the am half stands
    ("um acht Uhr nachts", "de", datetime(2017, 6, 28, 8, 0)),
    ("um sieben Uhr nachts", "de", datetime(2017, 6, 28, 7, 0)),
    # a 24-hour clock is as written
    ("um 23:30 nachts", "de", datetime(2017, 6, 27, 23, 30)),
    # nl reads the same way, with the night word joined to a digit clock
    ("om 11:00 's nachts", "nl", datetime(2017, 6, 27, 23, 0)),
    ("om elf uur 's nachts", "nl", datetime(2017, 6, 27, 23, 0)),
    ("om 3:00 's nachts", "nl", datetime(2017, 6, 28, 3, 0)),
]


@pytest.mark.parametrize("text,lang,start", NIGHT)
def test_night_word_picks_the_half_in_the_night(text, lang, start):
    res = extract_timespan(text, lang, ANCHOR)
    assert res is not None
    assert res.span.start == start
    assert res.remainder == ""


@pytest.mark.parametrize("text", ["um 15:30 nachts"])
def test_night_word_over_an_afternoon_hour_names_no_time(text):
    assert extract_timespan(text, "de", ANCHOR) is None
