# -*- coding: utf-8 -*-
"""A count with a weekday names that weekday in the period the count reaches, en.

"in two weeks on friday" is the Friday of the calendar week two weeks on,
and the week starts on the locale's first day: Monday for bare en and
Sunday for en-US (CLDR ``weekData/firstDay``).  "in a month on friday" is
the first Friday on or after the day the count reaches.  A count of days
reaches one day, so a weekday that is not that day's weekday names no day,
and the phrase is refused.  A weekday before a count of days stands apart
from it and keeps its own reading.  A deadline ("by friday") is not part of
the date the count names.

Anchor Saturday 2026-10-17 12:00.  Monday weeks run 12 to 18 October, then
19 to 25, then 26 October to 1 November; Sunday weeks run 11 to 17, then 18
to 24.  17 November 2026 is a Tuesday.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ad

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("lang,text,expected", [
    ("en", "in two weeks on friday", datetime(2026, 10, 30)),
    ("en", "friday in two weeks", datetime(2026, 10, 30)),
    ("en", "in a week on sunday", datetime(2026, 10, 25)),
    ("en-US", "in a week on sunday", datetime(2026, 10, 18)),
    ("en", "a week ago on friday", datetime(2026, 10, 9)),
    ("en", "in a month on friday", datetime(2026, 11, 20)),
    ("en", "in 2 days on monday", datetime(2026, 10, 19)),
])
def test_a_weekday_beside_a_count(lang, text, expected):
    r = extract_timespan(text, lang, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (
        ad(expected), ad(expected + timedelta(days=1)))
    assert r.remainder == ""


def test_a_count_of_days_with_another_weekday_is_refused():
    # Saturday plus three days is Tuesday 20, not a Monday.
    assert extract_timespan("in 3 days on monday", "en", SATURDAY) is None


def test_a_weekday_offset_keeps_its_own_reading():
    # "two weeks from friday" counts from the coming Friday, 23 October.
    r = extract_timespan("two weeks from friday", "en", SATURDAY)
    assert r.span.start == ad(datetime(2026, 11, 6))
    assert r.remainder == ""


def test_a_deadline_does_not_fold():
    # Saturday plus three days is Tuesday 20, at the anchor's clock.
    r = extract_timespan("in 3 days by friday", "en", SATURDAY)
    assert r is not None
    assert r.span.start == ad(datetime(2026, 10, 20, 12, 0))
    assert r.remainder == "by friday"


def test_a_weekday_before_a_count_of_days_keeps_the_count():
    # The coming Friday is 23 October.
    r = extract_timespan("friday in a day", "en", SATURDAY)
    assert r is not None
    assert r.span.start == ad(datetime(2026, 10, 23))
    assert r.remainder == "in a day"
