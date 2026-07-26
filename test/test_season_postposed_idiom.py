# -*- coding: utf-8 -*-
"""The postposed "last/next <season>" idiom resolves to the right year.

Regression guard for a silent-wrong fixed by making ``marker_position``
per-construction and adding ``season_ref`` to the postfix set: where a locale
postposes its season marker ("el verano pasado", "الصيف الماضي") the trailing
marker used to be STRANDED, so the phrase resolved to *this* season instead of
last/next.  Every phrase below is a native postposed form; the anchor
Tue 2017-06-27 sits inside the 2017 northern summer, so "last summer" is 2016
and "next summer" is 2018.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# (lang, phrase, expected start year).  Postposed "last summer" for every
# locale whose season marker genuinely trails (Romance, Semitic, Austronesian),
# plus postposed "next summer" where the locale has a native trailing form.
LAST_SEASON = [
    ("es", "el verano pasado", 2016),
    ("fr", "l'été dernier", 2016),
    ("pt", "o verão passado", 2016),
    ("it", "l'estate scorsa", 2016),
    ("ca", "l'estiu passat", 2016),
    ("gl", "o verán pasado", 2016),
    ("an", "o estiu pasau", 2016),
    ("ast", "el branu pasáu", 2016),
    ("oc", "l'estiu passat", 2016),
    ("mwl", "l berano passado", 2016),
    ("ar", "الصيف الماضي", 2016),
    ("he", "הקיץ שעבר", 2016),
    ("id", "musim panas lalu", 2016),
    ("ms", "musim panas lepas", 2016),
]

NEXT_SEASON = [
    ("es", "el verano que viene", 2018),
    ("fr", "l'été prochain", 2018),
    ("pt", "o verão que vem", 2018),
    ("it", "l'estate prossima", 2018),
    ("ca", "l'estiu vinent", 2018),
    ("ar", "الصيف المقبل", 2018),
]


@pytest.mark.parametrize("lang, phrase, year", LAST_SEASON)
def test_postposed_last_season_year(lang, phrase, year):
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None, f"{lang}: {phrase!r} did not parse"
    span, leftover = res
    assert span.start_datetime.year == year, (
        f"{lang}: {phrase!r} -> {span.start_datetime.year}, want {year} "
        f"(leftover {leftover!r})")
    assert not leftover.strip(), f"{lang}: stranded marker {leftover!r}"


@pytest.mark.parametrize("lang, phrase, year", NEXT_SEASON)
def test_postposed_next_season_year(lang, phrase, year):
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None, f"{lang}: {phrase!r} did not parse"
    span, leftover = res
    assert span.start_datetime.year == year, (
        f"{lang}: {phrase!r} -> {span.start_datetime.year}, want {year} "
        f"(leftover {leftover!r})")
    assert not leftover.strip(), f"{lang}: stranded marker {leftover!r}"


@pytest.mark.parametrize("lang, phrase, year", [
    ("es", "el verano de 2024", 2024),
    ("fr", "l'été 2024", 2024),
    ("pt", "o verão de 2024", 2024),
    ("it", "l'estate del 2024", 2024),
])
def test_season_of_year_still_resolves(lang, phrase, year):
    """No regression: the prefix "SEASON of YEAR" form still resolves."""
    res = extract_timespan(phrase, lang, ANCHOR)
    assert res is not None, f"{lang}: {phrase!r} did not parse"
    span, _ = res
    assert span.start_datetime.year == year
