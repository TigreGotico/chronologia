"""English counts read through numtag.

"two dozen" is 2 x 12 = 24, and "one thousand nine hundred and ninety nine" is
one number.  A quantifier ("a couple", "a few") is a count with its article.
Every expected value is written by hand or computed with ``relativedelta`` /
``timedelta`` from the anchor.
"""
import pytest

from chronologia import extract_duration

from ._corpus import ANCHOR, datetime, parse, relativedelta, span, timedelta


@pytest.mark.parametrize("text,expected", [
    ("two dozen years ago", ANCHOR - relativedelta(years=24)),
    ("three dozen days ago", ANCHOR - timedelta(days=36)),
    ("in two dozen days", ANCHOR + timedelta(days=24)),
])
def test_dozen_count(text, expected):
    assert span(text).start == expected
    assert parse(text).remainder == ""


def test_spelled_year_with_thousand_and_hundred():
    text = "in one thousand nine hundred and ninety nine"
    s = span(text)
    assert (s.start, s.end) == (datetime(1999, 1, 1), datetime(2000, 1, 1))
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,length", [
    ("a couple of weeks", timedelta(weeks=2)),
    ("a few days", timedelta(days=3)),
])
def test_article_before_a_quantifier_is_part_of_the_count(text, length):
    got = extract_duration(text, "en")
    assert got.duration == length
    assert got.remainder == ""
