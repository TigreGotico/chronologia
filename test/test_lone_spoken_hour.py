# -*- coding: utf-8 -*-
"""A lone spoken hour takes the next of its two twelve-hour readings.

An hour 1 to 12 said with no am/pm word and no part of the day is whichever of
h and h + 12 comes next at or after the anchor: "at 8" said at 15:00 is 20:00,
and "at 8" said at 06:00 is 08:00.  A day word or a part of the day keeps the
spoken hour, and so do a digit clock and an hour from 13 to 23.  A numeral with
no clock word and no clock preposition is no hour.

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime, timedelta, timezone

import pytest

from chronologia import extract_candidates, extract_timespan

AFTERNOON = datetime(2026, 3, 11, 15, 0)
MORNING = datetime(2026, 3, 11, 6, 0)
NOON = datetime(2026, 10, 17, 12, 0)
AFTER_NOON = datetime(2017, 6, 27, 13, 4)
ONE_THIRTY = datetime(2026, 3, 11, 13, 30)

# text, language, anchor, expected instant
LONE_HOURS = [
    ("at 8", "en", AFTERNOON, datetime(2026, 3, 11, 20, 0)),
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
    ("às 10 e meia", "pt", AFTER_NOON, datetime(2017, 6, 27, 22, 30)),
    ("dos quarts de deu", "ca", AFTERNOON, datetime(2026, 3, 11, 21, 30)),
    ("les deu i quart", "ca", AFTERNOON, datetime(2026, 3, 11, 22, 15)),
]

# text, language, anchor, expected instant: the spoken hour stands
KEPT = [
    ("tomorrow at 8", "en", AFTERNOON, datetime(2026, 3, 12, 8, 0)),
    ("at 8 pm", "en", MORNING, datetime(2026, 3, 11, 20, 0)),
    ("at 8 in the morning", "en", AFTERNOON, datetime(2026, 3, 12, 8, 0)),
    ("at 8:30", "en", AFTERNOON, datetime(2026, 3, 12, 8, 30)),
    ("at 20", "en", AFTERNOON, datetime(2026, 3, 11, 20, 0)),
    ("morgen om 8 uur", "nl", AFTER_NOON, datetime(2017, 6, 28, 8, 0)),
    ("at 0", "en", MORNING, datetime(2026, 3, 12, 0, 0)),
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


@pytest.mark.parametrize("text,lang,anchor,expected", LONE_HOURS)
def test_best_candidate_agrees_with_the_timespan(text, lang, anchor, expected):
    best = extract_candidates(text, lang, anchor)[0]
    assert best.span.start.datetime() == expected


@pytest.mark.parametrize("text,lang", [("7", "en"), ("20", "en"), ("7", "nl"),
                                       ("2", "nl")])
def test_a_lone_numeral_is_no_hour(text, lang):
    assert extract_timespan(text, lang, AFTERNOON) is None
