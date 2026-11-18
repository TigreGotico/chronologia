# -*- coding: utf-8 -*-
"""A lone spoken hour takes the next of its two twelve-hour readings.

An hour 1 to 12 said with no am/pm word and no part of the day is whichever of
h and h + 12 comes next at or after the anchor: "at 8" said at 15:00 is 20:00,
and "at 8" said at 06:00 is 08:00.  A day word or a part of the day keeps the
spoken hour, and so does an hour from 13 to 23.  A digit clock h:mm with an hour
from 1 to 11 reads like the spoken hour (test_digit_clock_lone_hour.py).  A
numeral with no clock word and no clock preposition is no hour.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime, timedelta, timezone

import pytest

from chronologia import (extract_candidates, extract_recurrence,
                         extract_timespan, extract_timespans)

AFTERNOON = datetime(2026, 3, 11, 15, 0)
MORNING = datetime(2026, 3, 11, 6, 0)
NOON = datetime(2026, 10, 17, 12, 0)
AFTER_NOON = datetime(2017, 6, 27, 13, 4)
ONE_THIRTY = datetime(2026, 3, 11, 13, 30)

# text, language, anchor, expected instant
LONE_HOURS = [
    ("at 8", "en", AFTERNOON, datetime(2026, 3, 11, 20, 0)),
    ("at 8:30", "en", AFTERNOON, datetime(2026, 3, 11, 20, 30)),
    ("at 8", "en", MORNING, datetime(2026, 3, 11, 8, 0)),
    ("at 12", "en", AFTERNOON, datetime(2026, 3, 12, 0, 0)),
    ("at 12", "en", MORNING, datetime(2026, 3, 11, 12, 0)),
    ("at 1", "en", ONE_THIRTY, datetime(2026, 3, 12, 1, 0)),
    ("wake me at 7", "en", MORNING, datetime(2026, 3, 11, 7, 0)),
    ("wake me at 7", "en", AFTERNOON, datetime(2026, 3, 11, 19, 0)),
    ("om 7 uur", "nl", AFTER_NOON, datetime(2017, 6, 27, 19, 0)),
    ("om half 9", "nl", AFTER_NOON, datetime(2017, 6, 27, 20, 30)),
    ("om kwart voor 1", "nl", NOON, datetime(2026, 10, 17, 12, 45)),
    ("alle tre e un quarto", "it", NOON, datetime(2026, 10, 17, 15, 15)),
    ("alle 11", "it", AFTER_NOON, datetime(2017, 6, 27, 23, 0)),
    ("om 12 uur", "nl", AFTER_NOON, datetime(2017, 6, 28, 0, 0)),
    ("at 12", "en", datetime(2017, 6, 27, 12, 0), datetime(2017, 6, 27, 12, 0)),
    ("at 8", "en", datetime(2026, 3, 11, 8, 0), datetime(2026, 3, 11, 8, 0)),
    ("às 10 e meia", "pt", AFTER_NOON, datetime(2017, 6, 27, 22, 30)),
    ("dos quarts de deu", "ca", AFTERNOON, datetime(2026, 3, 11, 21, 30)),
    ("les deu i quart", "ca", AFTERNOON, datetime(2026, 3, 11, 22, 15)),
]

# text, language, anchor, expected instant: the spoken hour stands
KEPT = [
    ("tomorrow at 8", "en", AFTERNOON, datetime(2026, 3, 12, 8, 0)),
    ("at 8 pm", "en", MORNING, datetime(2026, 3, 11, 20, 0)),
    ("at 8 am", "en", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("at 8 in the morning", "en", AFTERNOON, datetime(2026, 3, 12, 8, 0)),
    ("at 20", "en", AFTERNOON, datetime(2026, 3, 11, 20, 0)),
    ("morgen om 8 uur", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("at 0", "en", MORNING, datetime(2026, 3, 12, 0, 0)),
    ("at 10 o'clock in the morning", "en", AFTER_NOON, datetime(2017, 6, 28, 10, 0)),
    ("a las 10 en punto de la mañana", "es", AFTER_NOON, datetime(2017, 6, 28, 10, 0)),
    ("às 10 em ponto da manhã", "pt", AFTER_NOON, datetime(2017, 6, 28, 10, 0)),
    ("alle 10 in punto di mattina", "it", AFTER_NOON, datetime(2017, 6, 28, 10, 0)),
    ("ás 10 en punto da mañá", "gl", AFTER_NOON, datetime(2017, 6, 28, 10, 0)),
    ("à 10h et demie", "fr", AFTER_NOON, datetime(2017, 6, 28, 10, 30)),
    ("às 10h e meia", "pt", AFTER_NOON, datetime(2017, 6, 28, 10, 30)),
    ("às 10:00 e meia", "pt", AFTER_NOON, datetime(2017, 6, 28, 10, 30)),
    ("at 13", "en", AFTERNOON, datetime(2026, 3, 12, 13, 0)),
    ("at 8 utc+2", "en", AFTERNOON,
     datetime(2026, 3, 12, 8, 0, tzinfo=timezone(timedelta(hours=2)))),
]


@pytest.mark.parametrize("text,lang,anchor,expected", LONE_HOURS)
def test_lone_hour_is_the_next_twelve_hour_reading(text, lang, anchor,
                                                   expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == datetime(
        expected.year, expected.month, expected.day, expected.hour,
        expected.minute + 1)


@pytest.mark.parametrize("text,lang,anchor,expected", KEPT)
def test_a_marked_hour_keeps_the_spoken_hour(text, lang, anchor, expected):
    assert extract_timespan(text, lang, anchor).span.start.datetime() == expected


def test_an_unjoined_morning_word_beside_a_spoken_hour_keeps_the_morning():
    # "morgens" sits before the lead word, unjoined, and is the locale's am
    # word: it keeps the spoken hour 6 as the morning, not the evening.
    found = extract_timespan("morgens um 6", "de", AFTER_NOON)
    assert found.span.start.datetime() == datetime(2017, 6, 28, 6, 0)


@pytest.mark.parametrize("text,lang,anchor,expected", LONE_HOURS)
def test_best_candidate_agrees_with_the_timespan(text, lang, anchor, expected):
    best = extract_candidates(text, lang, anchor)[0]
    assert best.span.start.datetime() == expected


@pytest.mark.parametrize("text,lang", [("7", "en"), ("20", "en"), ("7", "nl"),
                                       ("2", "nl")])
def test_a_lone_numeral_is_no_hour(text, lang):
    assert extract_timespan(text, lang, AFTERNOON) is None


@pytest.mark.parametrize("text,rule", [
    ("daily at 7", "FREQ=DAILY;BYHOUR=7"),
    ("every monday at 7", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=7"),
    ("daily from 9 to 5", "FREQ=DAILY;BYHOUR=9"),
])
def test_a_recurrence_pin_keeps_the_spoken_hour(text, rule):
    found = extract_recurrence(text, "en", anchor=AFTERNOON)
    assert found[0].to_string() == rule


@pytest.mark.parametrize("text,lang,anchor,expected", LONE_HOURS)
def test_the_plural_api_reads_the_same_hour(text, lang, anchor, expected):
    found = extract_timespans(text, lang, anchor)
    assert found[0].span.start.datetime() == expected


@pytest.mark.parametrize("text,lang,anchor,expected", LONE_HOURS)
def test_no_candidate_keeps_the_morning_reading(text, lang, anchor, expected):
    candidates = extract_candidates(text, lang, anchor)
    assert candidates[0].span.start.datetime() == expected
    same_minute = {c.span.start.datetime() for c in candidates
                   if c.construction == "clock_time"
                   and c.span.start.minute == expected.minute}
    assert same_minute == {expected}
