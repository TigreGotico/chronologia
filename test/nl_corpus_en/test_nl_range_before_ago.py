"""A range of two counts before "ago" runs from the larger offset to the
smaller one: the unit and the "ago" after the second count measure both."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, ad, span


@pytest.mark.parametrize("text, far, near", [
    ("from two thousand to three thousand days ago",
     timedelta(days=3000), timedelta(days=2000)),
    ("between two thousand and three thousand days ago",
     timedelta(days=3000), timedelta(days=2000)),
    ("from 2000 to 3000 days ago",
     timedelta(days=3000), timedelta(days=2000)),
    ("from two to three hours ago",
     timedelta(hours=3), timedelta(hours=2)),
    ("between five and ten minutes ago",
     timedelta(minutes=10), timedelta(minutes=5)),
    ("between two and three weeks ago",
     timedelta(weeks=3), timedelta(weeks=2)),
])
def test_a_range_of_counts_before_ago_runs_from_the_larger_offset(
        text, far, near):
    found = extract_timespan(text, "en", ANCHOR)
    assert (found.span.start, found.span.end, found.remainder) == (
        ad(ANCHOR - far), ad(ANCHOR - near), "")


def test_a_range_of_years_before_ago_runs_between_the_two_points():
    """The two ends are the starts of the points "three thousand years ago"
    and "two thousand years ago"."""
    found = extract_timespan("from two thousand to three thousand years ago",
                             "en", ANCHOR)
    far = span("three thousand years ago")
    near = span("two thousand years ago")
    assert (found.span.start, found.span.end) == (far.start, near.start)
    assert found.remainder == ""


def test_a_reversed_range_before_ago_is_no_such_range():
    found = extract_timespan("from three to two days ago", "en", ANCHOR)
    assert found is None or found.span.end != ad(ANCHOR - timedelta(days=2))


def test_each_end_with_its_own_ago_keeps_its_own_offset():
    """"from 3 days ago to 2 days ago" names both offsets, the old reading."""
    found = extract_timespan("from 3 days ago to 2 days ago", "en", ANCHOR)
    assert found.span.start == ad(ANCHOR - timedelta(days=3))
