# -*- coding: utf-8 -*-
"""A four-digit hhmm with a leading zero before "hours" is a clock, no length.

"zero hundred hours" is 00:00 and "zero six hundred hours" is 06:00.  The
number layer folds them to "0000" and "0600", and the duration reader took the
folded number for a count of hours: zero hours, or 600 hours (25 days).  A
leading zero marks a clock, as "0600 hours" does when written in digits.  A
count without a leading zero ("600 hours") stays a length.

Every expected value is worked out by hand from the anchor, Friday 2026-01-30
10:00: the next 00:00 is Saturday 31 January and the next 06:00 follows it.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan
from chronologia.events import extract_event

ANCHOR = datetime(2026, 1, 30, 10, 0)

# text, expected clock
CLOCKS = [
    ("meet me at zero hundred hours", datetime(2026, 1, 31, 0, 0)),
    ("at zero hundred hours", datetime(2026, 1, 31, 0, 0)),
    ("zero hundred hours", datetime(2026, 1, 31, 0, 0)),
    ("at 0000 hours", datetime(2026, 1, 31, 0, 0)),
    ("at zero six hundred hours", datetime(2026, 1, 31, 6, 0)),
    ("at 0600 hours", datetime(2026, 1, 31, 6, 0)),
]


@pytest.mark.parametrize("text,expected", CLOCKS)
def test_a_military_time_is_no_length(text, expected):
    assert extract_duration(text, "en", anchor=ANCHOR) is None
    assert extract_timespan(text, "en", ANCHOR).span.start.datetime() \
        == expected


def test_the_event_is_the_clock_with_no_duration():
    event = extract_event("meet me at zero hundred hours", "en",
                          anchor=ANCHOR)
    assert event.span.start.datetime() == datetime(2026, 1, 31, 0, 0)
    assert event.duration is None
    assert event.summary == "meet me"


@pytest.mark.parametrize("text,expected", [
    ("600 hours", timedelta(days=25)),
    ("at 600 hours", timedelta(days=25)),
    ("2 hours", timedelta(hours=2)),
    ("meet me at zero hundred hours for 2 hours", timedelta(hours=2)),
])
def test_a_count_of_hours_stays_a_length(text, expected):
    assert extract_duration(text, "en", anchor=ANCHOR).duration == expected
