# -*- coding: utf-8 -*-
""""good evening" greets; it names no part of the day.

A greeting before a request must not turn into a band that strands the
request's own hour: "good evening, set an alarm at 7" is an hour, and the
greeting stays in the remainder.  Wiktionary lists "good evening", "good
night", "good morning" and "good afternoon" as interjections.  A part of the day
with no "good" before it still names its band.

Anchor: Friday 2026-09-25 12:00.  The lone hour 7 takes its next twelve-hour
reading after the anchor, 19:00 (ruling 17).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 9, 25, 12, 0)


@pytest.mark.parametrize("text,remainder", [
    ("good evening, set an alarm at 7", "good evening, set an alarm"),
    ("good night, set an alarm at 7", "good night, set an alarm"),
    ("good evenings, set an alarm at 7", "good evenings, set an alarm"),
    ("good morning, set an alarm at 7", "good morning, set an alarm"),
    ("good afternoon, wake me at 7", "good afternoon, wake me"),
])
def test_a_greeting_keeps_the_hour_of_the_request(text, remainder):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 9, 25, 19, 0)
    assert found.remainder == remainder


@pytest.mark.parametrize("text", ["good evening", "good night"])
def test_a_greeting_alone_is_no_time(text):
    assert extract_timespan(text, "en", ANCHOR) is None


@pytest.mark.parametrize("text,start,end", [
    ("tonight", datetime(2026, 9, 25, 21, 0), datetime(2026, 9, 26, 6, 0)),
    ("this evening", datetime(2026, 9, 25, 18, 0),
     datetime(2026, 9, 25, 21, 0)),
    ("evening", datetime(2026, 9, 25, 18, 0), datetime(2026, 9, 25, 21, 0)),
])
def test_a_part_of_the_day_without_good_keeps_its_band(text, start, end):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == start
    assert found.span.end.datetime() == end
