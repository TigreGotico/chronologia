# -*- coding: utf-8 -*-
"""Spanish spelled numbers that numtag reads whole.

A spelled year with "mil" ("dos mil veintiséis") is one number, so it reads
as a year after "en" and completes a date after "de".  Every expected value
is written by hand or computed with ``relativedelta`` from the anchor.
"""
import pytest

from ._corpus import datetime, parse, span


@pytest.mark.parametrize("text,year", [
    ("en dos mil veintiséis", 2026),
    ("en mil novecientos noventa y nueve", 1999),
    ("el año dos mil diez", 2010),
])
def test_spelled_year_with_mil(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "el veintiuno de marzo de dos mil veinte"
    s = span(text)
    assert (s.start, s.end) == (datetime(2020, 3, 21), datetime(2020, 3, 22))
    assert parse(text).remainder == ""
