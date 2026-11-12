"""A weekday beside a day word names the same day, or no day, en.

In "tomorrow, sunday" the weekday is an apposition to "tomorrow": it names
the same day, so it does not stay in the remainder.  "tomorrow monday" said
on a Saturday names no single day, and the reading is refused.

Anchor Saturday 2026-10-17 12:00; gold from datetime arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,offset", [
    ("tomorrow sunday", 1),
    ("tomorrow, sunday", 1),
    ("yesterday friday", -1),
    ("today saturday", 0),
])
def test_day_word_with_its_own_weekday(text, offset):
    day = SATURDAY.replace(hour=0) + timedelta(days=offset)
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert span.start == AstroDate(day.year, day.month, day.day)
    assert rest == ""


@pytest.mark.parametrize("text", ["tomorrow monday", "yesterday sunday"])
def test_day_word_with_another_weekday_is_refused(text):
    assert extract_timespan(text, "en", SATURDAY) is None
