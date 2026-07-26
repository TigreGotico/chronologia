# -*- coding: utf-8 -*-
"""Era and season references in Turkish."""
import pytest
from ._corpus import start, start_end, span, parse, AstroDate


@pytest.mark.parametrize("text,y", [
    ("44 mö", -43), ("753 mö", -752), ("323 mö", -322)])
def test_bc(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,y", [
    ("1492 ms", 1492), ("476 ms", 476), ("1071 ms", 1071)])
def test_ad(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,m", [
    ("yaz", 6), ("kış", 12), ("ilkbahar", 3), ("sonbahar", 9)])
def test_bare_season(text, m):
    # season resolves to a 3-month span starting on its first month
    s, e = start_end(text)
    assert (e - s).days >= 80


@pytest.mark.parametrize("text,start_ym,end_ym", [
    # Turkish year-first construction with the season taking the 3rd-person
    # possessive suffix ("2020's summer"): "2020 yazı" == "yaz 2020".
    ("2020 yazı", (2020, 6, 1), (2020, 9, 1)),
    ("2020 kışı", (2020, 12, 1), (2021, 3, 1)),
    ("2020 ilkbaharı", (2020, 3, 1), (2020, 6, 1)),
    ("2020 sonbaharı", (2020, 9, 1), (2020, 12, 1)),
    ("2020 güzü", (2020, 9, 1), (2020, 12, 1)),
])
def test_year_first_possessive_season(text, start_ym, end_ym):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    sp, rem = r
    assert rem == "", f"{text!r} left a remainder: {rem!r}"
    assert (sp.start_datetime.year, sp.start_datetime.month, sp.start_datetime.day) == start_ym
    assert (sp.end_datetime.year, sp.end_datetime.month, sp.end_datetime.day) == end_ym
