"""Spelled-out calendar years in English.

Three shapes reach the same year-wide span a digit year does:

* the scale composition -- "two thousand and one" (2001), "nineteen hundred
  and five" (1905).  It needs no cue: the digit form ``2001`` already reads as
  a year, so the spelled form must too;
* the year pair -- "nineteen ninety-nine" (1999), read *only* after an
  explicit year cue ("in ...", "the year ...") because a bare pair is
  genuinely ambiguous with a plain number;
* everything else refuses.  A malformed component, a scale word riding on the
  construction, or the deep-time "... years ago" frame yields no span at all
  rather than a fabricated year.
"""
import pytest

from ._corpus import AstroDate, nomatch, span, start


def _year(text, y):
    s = span(text)
    assert (s.start, s.end) == (AstroDate(y, 1, 1), AstroDate(y + 1, 1, 1))


# -- <n> thousand [and] <m> : no cue needed -------------------------------

@pytest.mark.parametrize("text,year", [
    ("two thousand and one", 2001),
    ("two thousand one", 2001),
    ("two thousand and twenty four", 2024),
    ("two thousand twenty four", 2024),
    ("two thousand", 2000),
    ("two thousand and ten", 2010),
    ("twelve thousand", 12000),
])
def test_thousand_composition(text, year):
    _year(text, year)


@pytest.mark.parametrize("text,year", [
    ("the year two thousand and one", 2001),
    ("in two thousand and one", 2001),
    ("the treaty of two thousand and one", 2001),
    ("the census of two thousand and eleven", 2011),
    ("she graduated in two thousand and twenty four", 2024),
])
def test_thousand_composition_in_context(text, year):
    _year(text, year)


# -- <n> hundred [and] <m> ------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("nineteen hundred", 1900),
    ("nineteen hundred and five", 1905),
    ("the year nineteen hundred", 1900),
    ("the strike of nineteen hundred and five", 1905),
    ("eighteen hundred and twelve", 1812),
])
def test_hundred_composition(text, year):
    _year(text, year)


# -- year pairs: cue required ---------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("in nineteen ninety-nine", 1999),
    ("the year nineteen ninety-nine", 1999),
    ("in nineteen eighty-four", 1984),
    ("I was born in nineteen eighty-four", 1984),
    ("the war ended in nineteen forty-five", 1945),
    ("in twenty twenty-four", 2024),
    ("the year twenty twenty-four", 2024),
    ("in nineteen ninety", 1990),
    ("in nineteen ninety nine", 1999),
])
def test_year_pair_with_cue(text, year):
    _year(text, year)


@pytest.mark.parametrize("text", [
    "nineteen ninety-nine",
    "twenty twenty-four",
    "nineteen eighty-four",
    "he scored nineteen ninety-nine points",
])
def test_bare_year_pair_is_not_a_year(text):
    """No cue, no year: a bare pair is ambiguous with a plain number."""
    nomatch(text)


# -- refusals --------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "two thousand and one hundred thousand",
    "ninety nine ninety nine",
    "thirteen fourteen",
    "in ninety nine",
    "in twenty five",
])
def test_refuses_rather_than_guesses(text):
    nomatch(text)


def test_ones_suffix_is_a_count_not_a_year():
    """"in twenty five days" is a count -- English spells 2005 with "oh"."""
    assert start("in twenty five days").day == 22
    assert start("in twenty five days").month == 7


# -- deep time and offsets survive ----------------------------------------

@pytest.mark.parametrize("text", [
    "66 million years ago", "sixty six million years ago",
])
def test_deep_time_unchanged(text):
    assert start(text) == AstroDate(-65_998_050, 1, 1)


def test_thousand_years_ago_is_still_deep_time():
    assert start("two thousand years ago") == AstroDate(-50, 1, 1)
    assert start("10 thousand years ago") == AstroDate(-8050, 1, 1)


def test_plain_offsets_unchanged():
    assert start("five days ago") == AstroDate(2017, 6, 22, 13, 4)
    assert start("in five days") == AstroDate(2017, 7, 2, 13, 4)
