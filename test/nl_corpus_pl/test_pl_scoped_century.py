# -*- coding: utf-8 -*-
"""The century named by an ordinal.

Polish writes the ordinal spelled out ("dwudziesty wiek", "drugi wiek")
or as a digit run with the trailing dot Polish uses for ordinals ("20.
wiek").  The century noun stays in the nominative singular; a count puts
it in the plural ("pięć wieków", "dwa wieki"), which names a quantity
rather than a period and must refuse.

Gold is arithmetic, not the parser: the Nth century opens in year
(N-1)*100 and is 100 years wide, half-open.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("20. wiek", 20),
    ("dwudziesty wiek", 20),
    ("drugi wiek", 2),
])
def test_the_nth_century_is_a_hundred_years(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["pięć wieków", "dwa wieki", "dwadzieścia wieków"])
def test_a_count_of_centuries_names_none_of_them(text):
    nomatch(text)


@pytest.mark.parametrize("text,n", [
    ("w 20. wieku", 20),
    ("w XX wieku", 20),
])
def test_in_the_nth_century_takes_the_locative(text, n):
    """The ordinary way to place an event in a century.

    "w" governs the locative, so the noun is "wieku" -- a form the century
    scope vocabulary did not list, which left "w 20." to be read as eight
    o'clock in the evening with "wieku" stranded.
    """
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


def test_mid_century_is_the_middle_third():
    """"w połowie XX wieku" -- the middle third of 1900..2000, cut at
    whole years: 1900 + 100/3 = 1933.3 and 1900 + 200/3 = 1966.7, each
    rounded to the nearest year."""
    s = span("w połowie XX wieku")
    assert (s.start.year, s.end.year) == (1933, 1967)
    assert parse("w połowie XX wieku")[1] == ""
