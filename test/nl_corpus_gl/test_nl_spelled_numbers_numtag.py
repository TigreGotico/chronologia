# -*- coding: utf-8 -*-
"""Galician spelled numbers that numtag reads whole.

A spelled year with "mil" ("dous mil vinte e seis") is one number, so it
reads as a year after "en" and completes a date after "de".  Every expected
value is written by hand.
"""
import pytest

from ._corpus import datetime, parse, span


@pytest.mark.parametrize("text,year", [
    ("en dous mil vinte e seis", 2026),
    ("en mil novecentos noventa e nove", 1999),
])
def test_spelled_year_with_mil(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "o vinte e un de marzo de dous mil vinte"
    s = span(text)
    assert (s.start, s.end) == (datetime(2020, 3, 21), datetime(2020, 3, 22))
    assert parse(text).remainder == ""
