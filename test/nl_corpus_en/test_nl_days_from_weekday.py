""""N days from <weekday>" counts whole days from the next occurrence of that
weekday, the way "a week from friday" already counts weeks.

Anchor: Tuesday 2017-06-27 13:04, so the next Friday is 2017-06-30.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse

FRIDAY = ANCHOR.replace(hour=0, minute=0, second=0) + timedelta(days=3)


@pytest.mark.parametrize("text,days", [
    ("2 days from friday", 2),
    ("two days from friday", 2),
    ("a fortnight from friday", 14),
    ("a week from friday", 7),
])
def test_day_units_from_a_weekday(text, days):
    res = parse(text)
    assert res is not None and res.remainder == "", f"{text!r} -> {res}"
    assert res[0].start == ad(FRIDAY + timedelta(days=days))
    assert res[0].end == ad(FRIDAY + timedelta(days=days + 1))


def test_a_calendar_unit_from_a_weekday_is_refused():
    """A month has no fixed length, so "two months from friday" names nothing."""
    assert parse("two months from friday") is None
