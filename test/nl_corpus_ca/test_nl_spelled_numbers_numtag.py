# -*- coding: utf-8 -*-
"""Catalan spelled numbers that numtag reads whole.

A spelled year with "mil" ("dos mil vint-i-sis") is one number, so it reads
as a year after "l'any" and "en", and completes a date after "de".  Every expected
value is written by hand.
"""
import pytest

from ._corpus import datetime, parse, span


@pytest.mark.parametrize("text,year", [
    ("l'any dos mil vint-i-sis", 2026),
    ("en mil nou-cents noranta-nou", 1999),
])
def test_spelled_year_with_mil(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "el vint-i-u de març de dos mil vint"
    s = span(text)
    assert (s.start, s.end) == (datetime(2020, 3, 21), datetime(2020, 3, 22))
    assert parse(text).remainder == ""
