# -*- coding: utf-8 -*-
"""A weekday of a relative week (English): the named day of the shifted week.

"<weekday> of next week" and "next week <weekday>" name a day inside the
shifted Monday-start week, not the bare weekday's next occurrence.  Every
anchor weekday is tried, because from a Saturday the two readings coincide
and hide the difference.  Expected days come from ``datetime.date``
arithmetic on the anchor, never from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import parse

CASES = [('friday of next week', 4, 1), ('the friday of next week', 4, 1), ('next week friday', 4, 1), ('friday next week', 4, 1), ('monday of last week', 0, -1), ('last week monday', 0, -1), ('wednesday of last week', 2, -1), ('saturday of next week', 5, 1), ('sunday of next week', 6, 1), ('tuesday of this week', 1, 0)]

# Monday 2026-10-19 and the six days after it.
ANCHORS = [datetime(2026, 10, 19 + i, 10, 0) for i in range(7)]


def _day(anchor, weekday, weeks):
    monday = anchor.date() - timedelta(days=anchor.weekday())
    return monday + timedelta(weeks=weeks, days=weekday)


@pytest.mark.parametrize("anchor", ANCHORS, ids=lambda a: a.strftime("%a"))
@pytest.mark.parametrize("text,weekday,weeks", CASES)
def test_weekday_of_relative_week(text, weekday, weeks, anchor):
    span, remainder = parse(text, anchor)
    want = _day(anchor, weekday, weeks)
    assert (span.start.year, span.start.month, span.start.day) == (
        want.year, want.month, want.day)
    assert (span.end - span.start).days == 1
    assert remainder == ""


def test_weekday_of_next_week_at_a_clock_time():
    anchor = datetime(2026, 10, 19, 10, 0)            # Monday
    span, remainder = parse("friday of next week at 9am", anchor)
    assert (span.start.year, span.start.month, span.start.day,
            span.start.hour, span.start.minute) == (2026, 10, 30, 9, 0)
    assert remainder == ""
    span, remainder = parse("friday next week at 9", anchor)
    assert (span.start.month, span.start.day, span.start.hour) == (10, 30, 9)
    assert remainder == ""


@pytest.mark.parametrize("anchor", ANCHORS, ids=lambda a: a.strftime("%a"))
def test_neighbouring_readings_are_unchanged(anchor):
    monday = anchor.date() - timedelta(days=anchor.weekday())

    def ymd(text):
        s = parse(text, anchor)[0]
        return date(s.start.year, s.start.month, s.start.day), (s.end - s.start).days

    assert ymd("next week") == (monday + timedelta(weeks=1), 7)
    assert ymd("last week") == (monday - timedelta(weeks=1), 7)
    assert ymd("this week") == (monday, 7)
    ahead = (4 - anchor.weekday()) % 7 or 7
    assert ymd("friday") == (anchor.date() + timedelta(days=ahead), 1)
    if anchor.weekday() <= 4:
        assert ymd("this friday") == (monday + timedelta(days=4), 1)
    back = (anchor.weekday() - 4) % 7 or 7
    assert ymd("last friday") == (anchor.date() - timedelta(days=back), 1)


def test_weekday_of_a_non_week_period_declines():
    anchor = datetime(2026, 10, 19, 10, 0)
    assert parse("friday of next month", anchor) is None
