"""'this <weekday>' names the coming one, or today when today is it.

Reading it as the weekday of the current calendar week put an already-past
weekday in the past: on a Tuesday, "this monday" answered yesterday while
the bare "monday" answered the following Monday, so the two disagreed about
the same day. Week start does not enter it -- that governs named calendar
periods such as "this week", not which occurrence of a weekday is meant.

Anchor 2017-06-27, a Tuesday.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


def test_an_already_past_weekday_names_the_coming_one():
    assert start("this monday") == _ad(date(2017, 7, 3))


def test_the_anchor_day_is_itself():
    assert start("this tuesday") == _ad(date(2017, 6, 27))


@pytest.mark.parametrize("text,expected", [
    ("this wednesday", date(2017, 6, 28)),
    ("this friday", date(2017, 6, 30)),
    ("this sunday", date(2017, 7, 2)),
])
def test_the_weekdays_still_ahead_are_unchanged(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    # the bare, next and last readings must all keep their own answers
    ("monday", date(2017, 7, 3)),
    ("next monday", date(2017, 7, 3)),
    ("last monday", date(2017, 6, 26)),
])
def test_the_other_weekday_markers_are_unchanged(text, expected):
    assert start(text) == _ad(expected)


def test_this_monday_agrees_with_the_bare_weekday():
    """The two disagreeing about the same day was the defect."""
    assert start("this monday") == start("monday")
