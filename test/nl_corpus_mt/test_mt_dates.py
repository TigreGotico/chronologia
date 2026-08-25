"""The Maltese date line: day, then month, then year.

CLDR states the order directly -- the long form is ``d 'ta'' MMMM y`` and the
numeric short form ``dd/MM/y`` -- so a Maltese date runs from the smallest
element to the largest, with the genitive linker ``ta'`` between the day and
the month name.  The day is a plain cardinal, not an ordinal, and the month
name takes no definite article.

Gold is the calendar itself: the date named is the date asserted.  Where the
year is left out, the locale prefers the future, so a date already past in
2027 lands in 2028 and one still ahead stays in 2027 -- the anchor is
2027-05-12.
"""
import pytest

from ._corpus import day, parse, remainder, start_end


@pytest.mark.parametrize("text,y,m,d", [
    ("15 ta' Awwissu 2027", 2027, 8, 15),
    ("25 ta' Diċembru 2020", 2020, 12, 25),
    ("1 ta' Jannar 2030", 2030, 1, 1),
    ("21 ta' Settembru 1964", 1964, 9, 21),
    ("8 ta' Diċembru 2019", 2019, 12, 8),
    ("31 ta' Marzu 2025", 2025, 3, 31),
    ("29 ta' Frar 2024", 2024, 2, 29),
    ("14 ta' Lulju 1789", 1789, 7, 14),
    ("7 ta' Ġunju 1919", 1919, 6, 7),
    ("30 ta' April 2026", 2026, 4, 30),
    ("2 ta' Novembru 2022", 2022, 11, 2),
    ("12 ta' Mejju 1990", 1990, 5, 12),
    ("3 ta' Ottubru 2031", 2031, 10, 3),
])
def test_the_date_line_runs_day_month_year(text, y, m, d):
    assert start_end(text) == day(y, m, d)


@pytest.mark.parametrize("text", [
    "15 ta' Awwissu 2027", "29 ta' Frar 2024", "12 ta' Mejju 1990",
])
def test_a_dated_line_is_wholly_consumed(text):
    assert remainder(text) == ""


# -- the linker is optional in practice, the order is not -------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15 Awwissu 2027", 2027, 8, 15),
    ("25 Diċembru 2020", 2020, 12, 25),
])
def test_the_genitive_linker_may_be_dropped(text, y, m, d):
    assert start_end(text) == day(y, m, d)


# -- no year: the future-preferring reading ---------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15 ta' Awwissu", 2027, 8, 15),
    ("25 ta' Diċembru", 2027, 12, 25),
    ("1 ta' Jannar", 2028, 1, 1),
    ("3 ta' Mejju", 2028, 5, 3),
    ("20 ta' Ġunju", 2027, 6, 20),
])
def test_a_yearless_date_prefers_the_future(text, y, m, d):
    assert start_end(text) == day(y, m, d)


# -- the abbreviated month names --------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("15 ta' Aww 2027", 2027, 8, 15),
    ("25 ta' Diċ 2020", 2020, 12, 25),
    ("1 ta' Jan 2030", 2030, 1, 1),
    ("6 ta' Ġun 2028", 2028, 6, 6),
])
def test_the_cldr_month_abbreviations(text, y, m, d):
    assert start_end(text) == day(y, m, d)


def test_the_march_abbreviation_is_not_shipped():
    # "mar" is the ordinary perfect of the verb mar, "to go", so it is left
    # out of the month vocabulary rather than turning a common verb into a
    # date.  The full name still reads.
    assert parse("3 ta' mar 2027") is None
    assert start_end("3 ta' Marzu 2027") == day(2027, 3, 3)


# -- the numeric forms ------------------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("30/06/2027", 2027, 6, 30),
    ("01/01/2030", 2030, 1, 1),
    ("2027-06-30", 2027, 6, 30),
])
def test_the_numeric_date_is_day_first(text, y, m, d):
    assert start_end(text) == day(y, m, d)


# -- bare years -------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("2019", 2019), ("1918", 1918), ("sena 2019", 2019),
])
def test_a_bare_year_is_the_whole_year(text, year):
    s = start_end(text)
    assert s[0].year == year and s[1].year == year + 1
