# -*- coding: utf-8 -*-
"""A weekday said on that same weekday names that day (Portuguese).

A day is a span, and a span that contains the anchor is the current one, as
a bare month said in that month is that month.  So "terça-feira" said on a
Tuesday is that Tuesday.  A time placed on that day that has already passed
is no longer ahead, so its next occurrence is meant: "terça às 10h" said at
13:04 is the next Tuesday.  A time still ahead stays on the day.  An
explicit "next" ("a próxima terça-feira") moves on a week, and an explicit "this"
("esta terça-feira") stays on the day, and so does a time on it that
has passed ("esta terça às 10h").

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
    ("terça-feira", TODAY),
    ("na terça", TODAY),
    ("terça às 15h", TODAY.replace(hour=15)),
    ("terça às 10h", TODAY.replace(hour=10) + WEEK),
    ("terça de manhã", TODAY.replace(hour=6) + WEEK),
    ("a próxima terça-feira", TODAY + WEEK),
    ("esta terça-feira", TODAY),
    ("esta terça às 10h", TODAY.replace(hour=10)),
    ("quarta-feira", TODAY + timedelta(days=1)),
])
def test_weekday_said_on_that_weekday(text, expected):
    result = extract_timespan(text, "pt", ANCHOR)
    assert result is not None, f"{text!r} did not parse"
    assert result[0].start == _ad(expected)
