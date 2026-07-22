# -*- coding: utf-8 -*-
"""Eras (לפנה״ס BC, לספירה AD), numeric deep time, seasons, fuzzy month thirds
and decades.  Hebrew has no conventional Before-Present marker (documented)."""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, start_end, span


@pytest.mark.parametrize("he,en", [
    ("44 לפנה״ס", "44 bc"),
    ("753 לפנה״ס", "753 bc"),
    ("1 לפנה״ס", "1 bc"),
    ("1492 לספירה", "1492 ad"),
    ("2024 לספירה", "2024 ad"),
    ("לפני 66 מיליון שנה", "66 million years ago"),
    ("לפני 4 מיליארד שנה", "4 billion years ago"),
])
def test_era_matches_en(he, en):
    a = extract_timespan(he, "he", ANCHOR)
    b = extract_timespan(en, "en", ANCHOR)
    assert a is not None, f"{he!r} did not parse"
    assert b is not None, f"{en!r} did not parse"
    assert (a[0].start, a[0].end) == (b[0].start, b[0].end)


@pytest.mark.parametrize("text,y0,y1", [
    ("44 לפנה״ס", -43, -42),
    ("1492 לספירה", 1492, 1493),
])
def test_era_absolute(text, y0, y1):
    ss, ee = start_end(text)
    assert ss == AstroDate(y0, 1, 1) and ee == AstroDate(y1, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("קיץ 1969", (1969, 6, 1), (1969, 9, 1)),
    ("חורף 1970", (1970, 12, 1), (1971, 3, 1)),
    ("אביב 2000", (2000, 3, 1), (2000, 6, 1)),
    ("סתיו 1989", (1989, 9, 1), (1989, 12, 1)),
])
def test_seasons(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,base", [
    ("שנות השמונים", 1980), ("שנות התשעים", 1990), ("שנות השישים", 1960),
    ("שנות השבעים", 1970),
])
def test_decades(text, base):
    ss, ee = start_end(text)
    assert ss == AstroDate(base, 1, 1) and ee == AstroDate(base + 10, 1, 1)


@pytest.mark.parametrize("text,month", [
    ("תחילת ינואר", 1), ("אמצע יולי", 7), ("סוף דצמבר", 12),
])
def test_month_fuzzy_within(text, month):
    sp = span(text)
    assert sp.start.month == month and sp.start.year == 2017
    assert sp.start < sp.end
