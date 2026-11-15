# -*- coding: utf-8 -*-
"""A weekday said on that same weekday names that day (Galician).

A day is a span, and a span that contains the anchor is the current one, as
a bare month said in that month is that month.  So "martes" said on a
Tuesday is that Tuesday.  A time placed on that day that has already passed
is no longer ahead, so its next occurrence is meant: "martes ás 10" said at
13:04 is the next Tuesday.  A time still ahead stays on the day.  An
explicit "next" ("o próximo martes") moves on a week, and an explicit "this"
("este martes") stays on the day.

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
    ("martes", TODAY),
    ("o martes", TODAY),
    ("martes ás 15", TODAY.replace(hour=15)),
    ("martes ás 10", TODAY.replace(hour=10) + WEEK),
    ("o martes pola mañá", TODAY.replace(hour=6) + WEEK),
    ("o próximo martes", TODAY + WEEK),
    ("este martes", TODAY),
    ("mércores", TODAY + timedelta(days=1)),
])
def test_weekday_said_on_that_weekday(text, expected):
    result = extract_timespan(text, "gl", ANCHOR)
    assert result is not None, f"{text!r} did not parse"
    assert result[0].start == _ad(expected)
