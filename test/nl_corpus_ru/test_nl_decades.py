"""Russian digit decades: "1980-е годы", "в 1980-х годах", "80-е".

Russian writes a decade as the numeral plus the hyphenated ordinal ending the
case calls for -- "80-е годы XX века", "70-80-е гг.", "1910-е гг." (Мильчин,
*Справочник издателя и автора*, §7.2.5) -- and that ending is what tells the
decade from the plain year "1980".  The framing "годы"/"годах" belongs to the
phrase, so it is consumed rather than left in the remainder.
"""
from datetime import timedelta

import pytest

from ._corpus import parse, span, start_end, nomatch, AstroDate


@pytest.mark.parametrize("text,y0", [
    ("1980-е годы", 1980),
    ("1980-е", 1980),
    ("в 1980-х годах", 1980),
    ("1990-е годы", 1990),
    ("1920-е годы", 1920),
    ("80-е годы", 1980),
    ("90-е", 1990),
])
def test_digit_decade(text, y0):
    assert start_end(text) == (AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_is_ten_years_wide():
    assert span("1980-е годы").width == timedelta(days=3653)


def test_framing_year_word_is_consumed():
    assert parse("1980-е годы").remainder == ""
    assert parse("восьмидесятые годы").remainder == ""


def test_bare_year_is_still_a_year():
    # no ordinal ending, so "1980" stays the single year
    assert start_end("1980") == (AstroDate(1980, 1, 1), AstroDate(1981, 1, 1))


def test_garbage_ending_is_no_decade():
    # a bogus ending names no decade: the digits fall back to the plain year
    # and the junk lands in the remainder rather than raising
    assert start_end("1980-щ ???") == (AstroDate(1980, 1, 1),
                                       AstroDate(1981, 1, 1))
    nomatch("щщщ ???")
