# -*- coding: utf-8 -*-
"""A weekday said on that same weekday names that day (English).

A day is a span, and a span that contains the anchor is the current one, as
a bare month said in that month is that month.  So "tuesday" said on a
Tuesday is that Tuesday.  A time placed on that day that has already passed
is no longer ahead, so its next occurrence is meant: "tuesday at 10am" said at
13:04 is the next Tuesday.  A time still ahead stays on the day.  An
explicit "next" ("next tuesday") moves on a week, and an explicit "this"
("this tuesday") stays on the day, and so does a time on it that
has passed ("this tuesday at 10am").

Anchor Tuesday 2017-06-27 13:04.  Gold comes from datetime arithmetic on the
anchor: the same day, or seven days later.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)
TODAY = ANCHOR.replace(hour=0, minute=0)
WEEK = timedelta(days=7)


def _ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


@pytest.mark.parametrize("text,expected", [
    ("tuesday", TODAY),
    ("on tuesday", TODAY),
    ("tuesday at 3pm", TODAY.replace(hour=15)),
    ("tuesday at 10am", TODAY.replace(hour=10) + WEEK),
    ("tuesday morning", TODAY.replace(hour=6) + WEEK),
    ("next tuesday", TODAY + WEEK),
    ("this tuesday", TODAY),
    ("this tuesday at 10am", TODAY.replace(hour=10)),
    ("wednesday", TODAY + timedelta(days=1)),
    ("tuesday at 1:03 pm", TODAY.replace(hour=13, minute=3) + WEEK),
    ("tuesday at 1:04 pm", TODAY.replace(hour=13, minute=4)),
    ("tuesday at 00:00", TODAY + WEEK),
])
def test_weekday_said_on_that_weekday(text, expected):
    result = extract_timespan(text, "en", ANCHOR)
    assert result is not None, f"{text!r} did not parse"
    assert result[0].start == _ad(expected)


def test_a_zoned_clock_on_that_weekday_is_compared_on_its_wall_clock():
    # "at 10am utc+2" on the anchor's Tuesday has passed by 13:04 on the
    # wall clock, so the next Tuesday is meant; the zone must not raise.
    result = extract_timespan("tuesday at 10am utc+2", "en", ANCHOR)
    assert result is not None
    start = result[0].start
    assert (start.year, start.month, start.day, start.hour) == (2017, 7, 4, 10)
