# -*- coding: utf-8 -*-
"""fr "deux heures de réunion" is a length even beside a date word and a part
of the day.

The clock reading must not take the "de" of "deux heures de réunion": "de"
belongs to a clock only before a part of the day ("deux heures de l'après-midi").
Taken with the clock, the "de" hid the count from the event reader, which read
02:00 and dropped the length.

Anchor: Friday 2026-01-30 10:00, so "demain" is 2026-01-31 and "lundi" is
2026-02-02.  Day values are calendar arithmetic by hand.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event, extract_timespan

ANCHOR = datetime(2026, 1, 30, 10)

LENGTHS = [
    ("demain deux heures de réunion le matin", datetime(2026, 1, 31),
     "réunion le matin"),
    ("lundi deux heures de cours l'après-midi", datetime(2026, 2, 2),
     "cours l après midi"),
    ("demain deux heures de réunion", datetime(2026, 1, 31), "réunion"),
]


@pytest.mark.parametrize("text,day,summary", LENGTHS)
def test_hours_of_a_noun_is_a_length(text, day, summary):
    event = extract_event(text, "fr", anchor=ANCHOR)
    assert event.duration == timedelta(hours=2)
    assert event.span.start.datetime() == day
    assert event.span.end.datetime() == day + timedelta(hours=2)
    assert event.summary == summary


@pytest.mark.parametrize("text,instant", [
    ("demain à deux heures de l'après-midi", datetime(2026, 1, 31, 14)),
    ("demain deux heures de l'après-midi", datetime(2026, 1, 31, 14)),
    ("demain à deux heures du matin", datetime(2026, 1, 31, 2)),
    ("demain à deux heures", datetime(2026, 1, 31, 2)),
])
def test_clock_with_a_part_of_the_day_stays_a_clock(text, instant):
    found = extract_timespan(text, "fr", ANCHOR)
    assert found.span.start.datetime() == instant
    assert found.remainder == ""
