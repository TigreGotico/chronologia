# -*- coding: utf-8 -*-
"""Portuguese spelled numbers that numtag reads whole.

A spelled year with "mil" ("dois mil e vinte e seis") and a count with a
collective noun ("duas dúzias") are one number each.  Every expected value is
written by hand or computed with ``relativedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, datetime, parse, relativedelta, span


@pytest.mark.parametrize("text,year", [
    ("em dois mil e vinte e seis", 2026),
    ("no ano de dois mil e vinte e seis", 2026),
    ("em mil novecentos e noventa e nove", 1999),
    ("no ano mil e quinhentos", 1500),
])
def test_spelled_year_with_mil(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "vinte e cinco de dezembro de dois mil e vinte e cinco"
    s = span(text)
    assert (s.start, s.end) == (datetime(2025, 12, 25), datetime(2025, 12, 26))
    assert parse(text).remainder == ""


def test_spelled_year_and_clock_half():
    text = "a 3 de março de dois mil e três às duas e meia"
    assert span(text).start == datetime(2003, 3, 3, 2, 30)
    assert parse(text).remainder == ""


def test_collective_noun_count():
    """Duas dúzias is 2 x 12 = 24 years."""
    text = "há duas dúzias de anos"
    assert span(text).start == ANCHOR - relativedelta(years=24)
    assert parse(text).remainder == ""
