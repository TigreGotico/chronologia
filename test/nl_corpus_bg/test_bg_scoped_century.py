# -*- coding: utf-8 -*-
"""The century named by an ordinal.

Bulgarian writes the ordinal either spelled out ("двадесети век",
"втори век") or as a digit, with or without the dot Bulgarian does not
require.  The century noun stays in the nominative singular; a count
takes the counting form instead ("пет века", "два века"), so a count
names a quantity, never a period, and must refuse.

Gold is arithmetic, not the parser: the Nth century opens in year
(N-1)*100 and is 100 years wide, half-open.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text,n", [
    ("20 век", 20),
    ("20. век", 20),
    ("двадесети век", 20),
    ("втори век", 2),
])
def test_the_nth_century_is_a_hundred_years(text, n):
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ["пет века", "два века"])
def test_a_count_of_centuries_names_none_of_them(text):
    nomatch(text)


@pytest.mark.parametrize("text,n", [
    ("през 20 век", 20),
    ("през 20. век", 20),
    ("в 20 век", 20),
])
def test_in_the_nth_century_reads_through_the_preposition(text, n):
    """"през 20 век" is how the century is ordinarily said.

    Bulgarian has no locative -- the noun keeps its nominative after the
    preposition -- so only the preposition itself had to be read.
    """
    s = span(text)
    assert (s.start.year, s.end.year) == ((n - 1) * 100, n * 100)
    assert parse(text)[1] == ""
