"""A named period is the calendar unit: "the 5th of this month" is the 5th of
the anchor's month even when that day has passed, while "the 5th of the month"
and "on the 5th" name the next 5th after the anchor.

Anchors: Tuesday 2017-06-27 13:04 and the 5th itself.  Gold values are read off
a calendar.
"""
from datetime import datetime

from ._corpus import parse


def test_this_month_keeps_the_anchors_month_after_the_day():
    r = parse("the 5th of this month")
    assert r[0].start == datetime(2017, 6, 5)
    assert r[1] == ""


def test_this_month_before_the_day():
    r = parse("the 30th of this month")
    assert r[0].start == datetime(2017, 6, 30)


def test_this_month_on_the_day_itself():
    r = parse("the 5th of this month", datetime(2017, 6, 5, 13, 4))
    assert r[0].start == datetime(2017, 6, 5)


def test_next_and_last_month_are_unchanged():
    assert parse("the 5th of next month")[0].start == datetime(2017, 7, 5)
    assert parse("the 5th of last month")[0].start == datetime(2017, 5, 5)


def test_unmarked_month_rolls_to_the_next_occurrence():
    assert parse("the 5th of the month")[0].start == datetime(2017, 7, 5)
    assert parse("on the 5th")[0].start == datetime(2017, 7, 5)
