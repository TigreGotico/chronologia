# -*- coding: utf-8 -*-
"""Italian spelled numbers that numtag reads whole.

Italian writes a number below a million as one word ("duemilaventisei",
"ventuno").  numtag reads the whole word, so a spelled year reads as a year
and "ventun giorni fa" counts 21 days.  Every expected value is written by
hand or computed with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, datetime, parse, span, timedelta


@pytest.mark.parametrize("text,year", [
    ("nel duemilaventisei", 2026),
    ("nel millenovecentonovantanove", 1999),
])
def test_spelled_year_in_one_word(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    s = span("il ventuno marzo duemilaventi")
    assert (s.start, s.end) == (datetime(2020, 3, 21), datetime(2020, 3, 22))


def test_apocopated_tens_and_one():
    """"ventun" is "ventuno" before a noun: 21 days."""
    text = "ventun giorni fa"
    assert span(text).start == ANCHOR - timedelta(days=21)
    assert parse(text).remainder == ""
