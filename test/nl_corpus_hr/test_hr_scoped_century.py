# -*- coding: utf-8 -*-
"""The century named by an ordinal.

Croatian writes an ordinal as a digit run with a trailing dot ("20.
stoljeće"), the same convention Czech, Slovak and Slovene use.  The
century noun stays in the nominative singular, which is what tells the
ordinal reading apart from a bare count: a count puts the noun in the
genitive plural instead ("pet stoljeća", "dva stoljeća"), so a count
names a quantity, never a period, and must refuse.

Gold is arithmetic, not the parser: the Nth century opens in year
(N-1)*100 and is 100 years wide, half-open.

The spelled-out ordinal ("dvadeseto stoljeće") is a separate vocabulary
gap -- Croatian's spelled ordinals are not listed -- and is not covered
here.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("20. stoljeće", 20),
    ("21. stoljeće", 21),
])
def test_the_nth_century_is_a_hundred_years(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["pet stoljeća", "dva stoljeća"])
def test_a_count_of_centuries_names_none_of_them(text):
    """"five centuries" is a quantity, not the fifth century."""
    nomatch(text)


@pytest.mark.parametrize("text,n", [
    ("u 20. stoljeću", 20),
    ("u 21. stoljeću", 21),
])
def test_in_the_nth_century_takes_the_locative(text, n):
    """The ordinary way to place an event in a century.

    "u" governs the locative, so the noun is "stoljeću", not the
    nominative "stoljeće" -- a form the century vocabulary did not list,
    which left "u 20." to be read as eight o'clock in the evening with the
    century noun stranded.
    """
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""
