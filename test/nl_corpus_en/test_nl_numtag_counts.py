"""English counts read through numtag.

"two dozen" is 2 x 12 = 24, and "one thousand nine hundred and ninety nine" is
one number.  A quantifier ("a couple", "a few") is a count with its article.
A half inside a count is part of it: "half a dozen" is 12 / 2 = 6.
Every expected value is written by hand or computed with ``relativedelta`` /
``timedelta`` from the anchor.
"""
import pytest

from chronologia import extract_duration

from ._corpus import (ANCHOR, AstroDate, datetime, parse, relativedelta,
                      span, start_end, timedelta)


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


@pytest.mark.parametrize("text,expected", [
    ("half a dozen days ago", ANCHOR - timedelta(days=6)),
    ("half a dozen weeks ago", ANCHOR - timedelta(weeks=6)),
    ("in half a dozen days", ANCHOR + timedelta(days=6)),
    # 12 + 12 / 2 = 18
    ("a dozen and a half days ago", ANCHOR - timedelta(days=18)),
])
def test_half_inside_a_count(text, expected):
    assert span(text).start == expected
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,years,width", [
    # 1 000 000 + 200 000, said to the thousand
    ("one million two hundred thousand years ago", 1_200_000, 1_000),
    # 1000 + 200, said to the hundred: numtag reads "one thousand two
    # hundred" as one number, as English joins its groups without "and"
    ("one thousand two hundred years ago", 1_200, 100),
    # 2 000 000 000 + 500 000 000, said to the million
    ("two billion five hundred million years ago", 2_500_000_000, 1_000_000),
    # 2.5 billion, said to a tenth of a billion
    ("two and a half billion years ago", 2_500_000_000, 100_000_000),
    # 0.5 million, said to a tenth of a million
    ("half a million years ago", 500_000, 100_000),
    # 2.5 million, said to a tenth of a million, the half before or after
    ("two and a half million years ago", 2_500_000, 100_000),
    ("two million and a half years ago", 2_500_000, 100_000),
])
def test_deep_time_count_with_several_scale_words(text, years, width):
    """The age is the whole number before "years": the start year is
    1950 - years before present, and the span is one unit of the last digit
    said wide."""
    assert start_end(text) == (AstroDate(1950 - years, 1, 1),
                               AstroDate(1950 - years + width, 1, 1))
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,expected,left", [
    ("I finished chapter one two days ago", ANCHOR - timedelta(days=2),
     "I finished chapter one"),
    ("chapter one, two days ago", ANCHOR - timedelta(days=2), "chapter one"),
    ("I watched season one two weeks ago", ANCHOR - timedelta(weeks=2),
     "I watched season one"),
    ("I beat level three two hours ago", ANCHOR - timedelta(hours=2),
     "I beat level three"),
    ("we moved to room four three days ago", ANCHOR - timedelta(days=3),
     "we moved to room four"),
    ("bus number seven ten minutes ago", ANCHOR - timedelta(minutes=10),
     "bus number seven"),
    ("platform nine three minutes from now", ANCHOR + timedelta(minutes=3),
     "platform nine"),
    ("gate twelve five minutes from now", ANCHOR + timedelta(minutes=5),
     "gate twelve"),
])
def test_a_number_that_names_a_thing_leaves_the_count_after_it(
        text, expected, left):
    """Only a number that ends in a scale word and a smaller number make a
    pair ("mil duzentos"): "chapter one" names the chapter, and "two days
    ago" is the count."""
    got = parse(text)
    assert got.span.start == expected
    assert got.remainder == left


def test_a_length_after_a_number_that_names_a_thing():
    got = extract_duration("level three two hours", "en")
    assert got.duration == timedelta(hours=2)
    assert got.remainder == "level three"
