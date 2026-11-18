# -*- coding: utf-8 -*-
"""fr "deux heures moins le quart" is a length of 1 h 45 min.

A count of hours takes a fraction off with "moins le quart" as it adds one
with "et quart": "deux heures et quart" is 2 h 15 min and "deux heures moins le
quart" is 1 h 45 min.  The length reader left "moins le quart" behind, so the
event summary read "réunion de moins le quart" and the length was 2 h.

Anchor: Friday 2026-01-30 10:00, so "demain" is 2026-01-31.  The lengths are
hand arithmetic: 2 h less a quarter of an hour (15 min) is 105 min.  The start
is the CLDR morning band for fr, 04:00 (``chronologia/dayparts.py``).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_event, extract_timespan

ANCHOR = datetime(2026, 1, 30, 10)
TOMORROW = datetime(2026, 1, 31)


@pytest.mark.parametrize("text,start", [
    ("réunion de deux heures moins le quart le matin demain",
     TOMORROW + timedelta(hours=4)),
    ("réunion de deux heures moins le quart demain", TOMORROW),
    ("réunion deux heures moins le quart demain", TOMORROW),
])
def test_event_length_takes_the_quarter_off(text, start):
    event = extract_event(text, "fr", anchor=ANCHOR)
    assert event.duration == timedelta(minutes=105)
    assert event.span.start.datetime() == start
    assert event.summary == "réunion"


@pytest.mark.parametrize("text,length,remainder", [
    ("deux heures moins le quart", timedelta(minutes=105), ""),
    ("trois heures moins le quart", timedelta(minutes=165), ""),
    ("deux heures et quart", timedelta(minutes=135), ""),
])
def test_duration_reads_the_fraction(text, length, remainder):
    found = extract_duration(text, "fr", anchor=ANCHOR)
    assert found.duration == length
    assert found.remainder == remainder


@pytest.mark.parametrize("text,instant", [
    ("réunion de trois heures moins dix demain",
     datetime(2026, 1, 31, 2, 50)),
    ("deux heures moins le quart demain", datetime(2026, 1, 31, 1, 45)),
])
def test_minutes_and_clock_stay_a_clock(text, instant):
    assert extract_timespan(text, "fr", ANCHOR).span.start.datetime() == instant
