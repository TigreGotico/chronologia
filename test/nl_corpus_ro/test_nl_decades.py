"""Romanian decade references: "anii 1980", "anii '80", "anii optzeci".

The definite plural "anii" in front of a whole ten is the Romanian decade
frame -- DEX '09 glosses *optzecist* as "scriitor din generația anilor '80 ai
sec. XX", the 1980-1989 decade -- so "anii 1980" is the decade, never the
single year 1980.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y0", [
    ("anii 1980", 1980),
    ("anii 1990", 1990),
    ("anii 1920", 1920),
    ("anii 80", 1980),
    ("în anii 1970", 1970),
])
def test_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_is_ten_years_wide():
    assert span("anii 1980").width == timedelta(days=3653)


@pytest.mark.parametrize("text,y0", [
    ("anii optzeci", 1980),
    ("anii nouăzeci", 1990),
    ("anii treizeci", 1930),
    ("în anii șaptezeci", 1970),
])
def test_spelled_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_bare_cardinal_is_still_a_number():
    # "optzeci de ani" counts eighty years; it is not the eighties
    nomatch("optzeci de euro")


def test_bare_year_is_still_a_year():
    assert start_end("în 1980") == (AstroDate(1980, 1, 1),
                                    AstroDate(1981, 1, 1))


def test_garbage_does_not_raise():
    nomatch("anii ???")
