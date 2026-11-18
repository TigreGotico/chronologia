# -*- coding: utf-8 -*-
"""French spelled numbers that numtag reads whole.

A spelled year with "mille" ("deux mille vingt-six") is one number, so it
reads as a year after "en" and completes a date.  Belgian and Swiss French
name 70 and 90 "septante" and "nonante", and Swiss French names 80
"huitante": "Ils sont officiels en Belgique et en Suisse", "octante, qui a
été supplanté par quatre-vingts et huitante" (Académie française, Questions
de langue, "Septante, octante (ou huitante), nonante",
https://www.dictionnaire-academie.fr/article/QDL078).  The fr-BE and fr-CH
tags read them with numtag's lexicon of the region.  Every expected value is
written by hand or computed with ``relativedelta`` from the anchor.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, datetime, parse, relativedelta, span, timedelta


@pytest.mark.parametrize("text,year", [
    ("en deux mille vingt-six", 2026),
    ("en mille neuf cent quatre-vingt-dix-neuf", 1999),
])
def test_spelled_year_with_mille(text, year):
    s = span(text)
    assert (s.start, s.end) == (datetime(year, 1, 1), datetime(year + 1, 1, 1))
    assert parse(text).remainder == ""


def test_spelled_year_completes_a_date():
    text = "le vingt et un mars deux mille vingt"
    s = span(text)
    assert (s.start, s.end) == (datetime(2020, 3, 21), datetime(2020, 3, 22))
    assert parse(text).remainder == ""


@pytest.mark.parametrize("lang,text,expected", [
    ("fr-BE", "il y a septante ans", ANCHOR - relativedelta(years=70)),
    ("fr-CH", "il y a huitante ans", ANCHOR - relativedelta(years=80)),
    ("fr-BE", "dans nonante jours", ANCHOR + timedelta(days=90)),
    ("fr-BE", "en mille neuf cent septante-cinq", datetime(1975, 1, 1)),
])
def test_regional_tens(lang, text, expected):
    r = extract_timespan(text, lang, ANCHOR)
    assert r.span.start.datetime() == expected
    assert r.remainder == ""
