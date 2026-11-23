# -*- coding: utf-8 -*-
"""A clock beside "the day after next" or "the day before last" is its time.

"the day after next" is two days on from the anchor and "the day before last"
two days back, so "the day after next 3 pm" is 15:00 on that day, as "the day
after tomorrow 3 pm" is.  A part of the day in the phrase ("the morning after
next") is a band of its day, and a clock beside it may contradict the band, so
the clock stays unread there.  The bands are the CLDR en day periods: morning
06:00 to 12:00 and evening 18:00 to 21:00.

Every expected instant is worked out by hand from the anchor, Friday
2026-01-30 10:00: two days on is Sunday 1 February, two days back is
Wednesday 28 January.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.events import extract_event

ANCHOR = datetime(2026, 1, 30, 10, 0)
SUNDAY_3PM = datetime(2026, 2, 1, 15, 0)

# text, expected instant
CLOCKS = [
    ("the day after next 3 pm", SUNDAY_3PM),
    ("the day after next at 3 pm", SUNDAY_3PM),
    ("the day after next, 3 pm", SUNDAY_3PM),
    ("the day after next 15:00", SUNDAY_3PM),
    ("3 pm the day after next", SUNDAY_3PM),
    ("the day after next at noon", datetime(2026, 2, 1, 12, 0)),
    ("the day before last 3 pm", datetime(2026, 1, 28, 15, 0)),
    ("the day before last at 9 am", datetime(2026, 1, 28, 9, 0)),
]


@pytest.mark.parametrize("text,expected", CLOCKS)
def test_the_clock_places_on_the_day_the_idiom_names(text, expected):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == datetime(
        expected.year, expected.month, expected.day, expected.hour,
        expected.minute + 1)
    assert found.remainder == ""


def test_the_event_keeps_the_clock_out_of_the_summary():
    event = extract_event("the day after next 3 pm", "en", anchor=ANCHOR)
    assert event.span.start.datetime() == SUNDAY_3PM
    assert event.summary == ""


def test_the_day_after_next_alone_is_the_whole_day():
    found = extract_timespan("the day after next", "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 2, 1)
    assert found.span.end.datetime() == datetime(2026, 2, 2)


@pytest.mark.parametrize("text,start,end,remainder", [
    ("the morning after next at 3 pm", datetime(2026, 2, 1, 6),
     datetime(2026, 2, 1, 12), "at 3 pm"),
    ("the evening after next 8 pm", datetime(2026, 2, 1, 18),
     datetime(2026, 2, 1, 21), "8 pm"),
])
def test_a_part_of_the_day_in_the_idiom_leaves_the_clock_unread(
        text, start, end, remainder):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == start
    assert found.span.end.datetime() == end
    assert found.remainder == remainder


@pytest.mark.parametrize("text", [
    "the week before last at 3 pm",
    "the month before last at 3 pm",
    "the year before last at noon",
])
def test_a_period_before_last_takes_no_clock(text):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.end.datetime() - found.span.start.datetime() \
        >= datetime(2026, 1, 8) - datetime(2026, 1, 1)
    assert found.remainder.startswith("at ")
