"""Filipino dates, which draw on both numeral systems inside one expression.

The sourced worked example is "Ika-isa ng Abril, taong dalawang libo't
dalawampu't dalawa" (1 April 2022): the day is a NATIVE ordinal under the
``ika-`` prefix, the month is the Spanish-derived loan NAME (not a counted
numeral at all), and the year is spelled out in NATIVE cardinals.  The same
source also gives the month-first ordering, "Abril (ika-)isa, ...", so both
templates ship.  Order is day-month-year throughout.
"""
from datetime import date

import pytest

from ._corpus import nomatch, span, start


@pytest.mark.parametrize("text,y,m,d", [
    ("ika-24 ng Agosto 2026", 2026, 8, 24),
    ("ika-isa ng Abril 2022", 2022, 4, 1),
    ("ika-25 ng Disyembre 2026", 2026, 12, 25),
    ("ika-31 ng Disyembre 2099", 2099, 12, 31),
    ("ika-15 ng Pebrero 2020", 2020, 2, 15),
])
def test_day_ordinal_then_month_then_year(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("Abril ika-isa 2022", 2022, 4, 1),
    ("Agosto ika-24 2026", 2026, 8, 24),
])
def test_month_first_template(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("ika-isa ng Abril taong dalawang libo't dalawampu't dalawa",
     2022, 4, 1),
    ("Abril ika-isa taong dalawang libo't dalawampu't dalawa", 2022, 4, 1),
    ("ika-25 ng Disyembre taong dalawang libo't dalawampu", 2020, 12, 25),
])
def test_the_year_is_spelled_in_native_numerals(text, y, m, d):
    """One expression, three slots, two numeral systems: native ordinal day,
    Spanish loan month name, native cardinal year."""
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,d", [
    ("ikaisa ng Hulyo 2020", 1), ("ikalawa ng Hulyo 2020", 2),
    ("ikatlo ng Hulyo 2020", 3), ("ikaapat ng Hulyo 2020", 4),
    ("ikalima ng Hulyo 2020", 5), ("ikaanim ng Hulyo 2020", 6),
    ("ikapito ng Hulyo 2020", 7), ("ikawalo ng Hulyo 2020", 8),
    ("ikasiyam ng Hulyo 2020", 9), ("ikasampu ng Hulyo 2020", 10),
    ("ikalabing-isa ng Hulyo 2020", 11),
    ("ikalabindalawa ng Hulyo 2020", 12),
    ("ikalabintatlo ng Hulyo 2020", 13),
    ("ikalabing-apat ng Hulyo 2020", 14),
    ("ikalabinlima ng Hulyo 2020", 15),
    ("ikadalawampu ng Hulyo 2020", 20),
])
def test_the_solid_ordinal_spellings(text, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (2020, 7, d)


@pytest.mark.parametrize("text,d", [
    ("ika-isa ng Hulyo 2020", 1), ("ika-apat ng Hulyo 2020", 4),
    ("ika-lima ng Hulyo 2020", 5), ("ika-anim ng Hulyo 2020", 6),
    ("ika-pito ng Hulyo 2020", 7), ("ika-walo ng Hulyo 2020", 8),
    ("ika-siyam ng Hulyo 2020", 9), ("ika-sampu ng Hulyo 2020", 10),
])
def test_the_separated_ordinal_spelling(text, d):
    """The source writes the prefix with a hyphen ("ika-24", "ika-apat"); the
    tokenizer shears it, so the fold rejoins the two pieces."""
    s = start(text)
    assert (s.year, s.month, s.day) == (2020, 7, d)


MONTHS = ["enero", "pebrero", "marso", "abril", "mayo", "hunyo", "hulyo",
          "agosto", "setyembre", "oktubre", "nobyembre", "disyembre"]


@pytest.mark.parametrize("name,number", list(zip(MONTHS, range(1, 13))))
def test_every_month_name(name, number):
    s = start(f"ika-10 ng {name} 2021")
    assert (s.year, s.month, s.day) == (2021, number, 10)


@pytest.mark.parametrize("name,number", list(zip(MONTHS, range(1, 13))))
def test_a_bare_month_is_the_whole_month(name, number):
    s = span(f"{name} 2021")
    assert s.start.month == number
    assert (s.end.year, s.end.month) == \
        (2021 + (number == 12), number % 12 + 1)


def test_the_day_ordinal_and_the_hour_ordinal_are_the_same_construction():
    """``ika-`` builds both, so only the surrounding words tell them apart --
    ``ng`` plus a month name makes it a date, ``ng`` plus a day-part an hour."""
    assert start("ika-apat ng Hulyo 2020").day == 4
    assert start("ika-apat ng hapon").hour == 16


def test_a_bare_ordinal_names_no_date():
    """With neither a month nor a day-part after it, ``ika-apat`` is only the
    number four and names nothing."""
    nomatch("ika-apat")
