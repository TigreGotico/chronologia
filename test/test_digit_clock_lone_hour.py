# -*- coding: utf-8 -*-
"""A digit clock from speech follows the lone-hour rule.

Speech recognition writes a spoken "three thirty" as "3:30", so the two forms
read the same.  A digit clock h:mm with an hour 1 to 11, no leading zero, no
am/pm word and no part of the day is whichever of its two twelve-hour readings
comes next after the anchor.  A leading zero, the hour 12, an hour 13 to 23, an
am/pm word and a part of the day read as written.  "Today" names no part of the
day; any other day word keeps the written hour.  A locale's own morning or
evening word beside the clock, even unjoined, decides the half: an evening word
pins the pm reading, a morning or night word keeps the written hour.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime

import pytest

from chronologia import (extract_candidates, extract_recurrence,
                         extract_timespan, extract_timespans)

AFTERNOON = datetime(2026, 3, 11, 15, 0)
MORNING = datetime(2026, 3, 11, 6, 0)
AFTER_NOON = datetime(2017, 6, 27, 13, 4)

# text, language, anchor, expected instant
NEXT_READING = [
    ("wake me up at 6:30", "en", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("at 3:30", "en", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("at 3:30 today", "en", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("at 6:30", "en", MORNING, datetime(2026, 3, 11, 6, 30)),
    ("at 6:30", "en", datetime(2026, 3, 11, 7, 0),
     datetime(2026, 3, 11, 18, 30)),
    ("at 1:45", "en", datetime(2026, 10, 23, 13, 10),
     datetime(2026, 10, 23, 13, 45)),
    ("at 10:30", "en", datetime(2026, 10, 23, 11, 59),
     datetime(2026, 10, 23, 22, 30)),
    ("at 11:30", "en", datetime(2026, 10, 23, 23, 45),
     datetime(2026, 10, 24, 11, 30)),
    ("lembra-me às 3:30", "pt", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("lembra-me às 6:30", "pt", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("a las 3:30", "es", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("a las 6:30", "es", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("um 3:30", "de", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("um 6:30", "de", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("à 3:30", "fr", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("à 6:30", "fr", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("alle 3:30", "it", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("alle 6:30", "it", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("om 3:30", "nl", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("om 6:30", "nl", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("a les 3:30", "ca", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("a les 6:30", "ca", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("ás 3:30", "gl", AFTERNOON, datetime(2026, 3, 11, 15, 30)),
    ("ás 6:30", "gl", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
]

# text, language, anchor, expected instant: the written hour stands
AS_WRITTEN = [
    ("tomorrow at 6:30", "en", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("at 03:30", "en", AFTERNOON, datetime(2026, 3, 12, 3, 30)),
    ("at 12:30", "en", AFTERNOON, datetime(2026, 3, 12, 12, 30)),
    ("at 15:30", "en", datetime(2026, 3, 11, 14, 0),
     datetime(2026, 3, 11, 15, 30)),
    ("at 18:30", "en", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("at 6:30 am", "en", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("at 6:30 pm", "en", MORNING, datetime(2026, 3, 11, 18, 30)),
    ("at 6:30 in the morning", "en", AFTER_NOON,
     datetime(2017, 6, 28, 6, 30)),
    ("às 3:30 da manhã", "pt", AFTERNOON, datetime(2026, 3, 12, 3, 30)),
    ("às 03:30", "pt", AFTERNOON, datetime(2026, 3, 12, 3, 30)),
    ("amanhã às 6:30", "pt", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("à 9h30", "fr", AFTER_NOON, datetime(2017, 6, 28, 9, 30)),
    ("às 9h05", "pt", AFTER_NOON, datetime(2017, 6, 28, 9, 5)),
    # fil has no am/pm vocabulary: the word is left over and the hour stays
    ("6:05 am", "fil", AFTER_NOON, datetime(2017, 6, 28, 6, 5)),
    # a locale's own morning word, even unjoined, keeps the written hour
    ("om 8:00 's ochtends", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("om 8:00 's morgens", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("'s ochtends om 8:00", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("om 8:00 uur 's ochtends", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("morgens um 6:30", "de", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("um 6:30 Uhr morgens", "de", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("madrugada a las 4:30", "es", AFTER_NOON, datetime(2017, 6, 28, 4, 30)),
]

# text, language, anchor, expected instant: an evening word pins the pm half
EVENING = [
    ("om 8:00 's avonds", "nl", AFTER_NOON, datetime(2017, 6, 27, 20, 0)),
    ("om 8:00 's avonds", "nl", datetime(2017, 6, 27, 23, 0),
     datetime(2017, 6, 28, 20, 0)),
    ("tarde a las 4:30", "es", AFTER_NOON, datetime(2017, 6, 27, 16, 30)),
    ("tarde a las 4:30", "es", datetime(2017, 6, 27, 3, 0),
     datetime(2017, 6, 27, 16, 30)),
]


@pytest.mark.parametrize("text,lang,anchor,expected", NEXT_READING)
def test_a_digit_clock_takes_the_next_twelve_hour_reading(text, lang, anchor,
                                                          expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == datetime(
        expected.year, expected.month, expected.day, expected.hour,
        expected.minute + 1)


@pytest.mark.parametrize("text,lang,anchor,expected", AS_WRITTEN)
def test_a_marked_digit_clock_reads_as_written(text, lang, anchor, expected):
    assert extract_timespan(text, lang, anchor).span.start.datetime() == expected


@pytest.mark.parametrize("text,lang,anchor,expected", EVENING)
def test_an_evening_word_moves_a_digit_clock_to_the_pm_half(text, lang, anchor,
                                                            expected):
    assert extract_timespan(text, lang, anchor).span.start.datetime() == expected


@pytest.mark.parametrize("text,lang,anchor,expected", NEXT_READING)
def test_the_other_apis_read_the_same_digit_clock(text, lang, anchor, expected):
    assert extract_timespans(text, lang, anchor)[0].span.start.datetime() \
        == expected
    assert extract_candidates(text, lang, anchor)[0].span.start.datetime() \
        == expected


def test_a_spoken_hour_and_its_digit_clock_agree():
    spoken = extract_timespan("at three thirty", "en", AFTERNOON)
    digit = extract_timespan("at 3:30", "en", AFTERNOON)
    assert spoken.span.start.datetime() == digit.span.start.datetime()


def test_a_recurrence_pin_keeps_the_written_digit_hour():
    found = extract_recurrence("daily at 6:30", "en", anchor=AFTER_NOON)
    assert found[0].to_string() == "FREQ=DAILY;BYHOUR=6;BYMINUTE=30"


def test_today_never_moves_to_tomorrow():
    found = extract_timespan("at 3:30 today", "en",
                             datetime(2017, 6, 27, 23, 0))
    assert found.span.start.datetime() == datetime(2017, 6, 27, 3, 30)
