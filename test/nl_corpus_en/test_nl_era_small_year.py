# -*- coding: utf-8 -*-
"""Era-marked years below the day-of-month ceiling.

A bare numeral must clear 32 before it reads as a year, because 1..31 is
also a day of the month.  An explicit BC/AD marker removes that ambiguity
outright: "march 15th, 31 bc" has its day slot already filled and a marker
that only a year can carry.  Without the marker bound the month-day reading
wins alone, and the answer is the next occurrence of march 15th -- roughly
two thousand years the wrong way, with the era stranded in the remainder.

Golds are hand-derived: astronomical year numbering has no year zero, so
N BC is the astronomical year 1 - N (31 BC is -30, 1 BC is 0), while N AD
is simply the year N with no two-digit-century pivot.
"""
import pytest

from ._corpus import AstroDate, parse, span, start_end


@pytest.mark.parametrize("text,bc_year", [
    ('march 15th, 1 bc', 1),
    ('march 15th, 2 bc', 2),
    ('march 15th, 5 bc', 5),
    ('march 15th, 12 bc', 12),
    ('march 15th, 31 bc', 31),
    ('march 15th, 32 bc', 32),          # already worked -- the old floor
    ('march 15th, 44 bc', 44),          # the ides of march
    ('15th of march 31 bc', 31),
    ('march 15th 31 bce', 31),
])
def test_calendar_date_small_bc_year(text, bc_year):
    s, e = start_end(text)
    assert s == AstroDate(1 - bc_year, 3, 15)
    assert e == AstroDate(1 - bc_year, 3, 16)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,year", [
    ('march 15th, 5 ad', 5),
    ('march 15th, 12 ad', 12),
    ('march 15th, 31 ad', 31),
    ('march 15th, 44 ad', 44),
])
def test_calendar_date_small_ad_year(text, year):
    """An AD marker names the year outright -- no two-digit-century pivot."""
    s, e = start_end(text)
    assert s == AstroDate(year, 3, 15)
    assert e == AstroDate(year, 3, 16)
    assert parse(text)[1] == ""


def test_january_first_five_bc():
    s, e = start_end('january 1st, 5 bc')
    assert (s, e) == (AstroDate(-4, 1, 1), AstroDate(-4, 1, 2))
    assert parse('january 1st, 5 bc')[1] == ""


@pytest.mark.parametrize("text,start_,end_", [
    ('the first quarter of 5 bc', AstroDate(-4, 1, 1), AstroDate(-4, 4, 1)),
    ('q1 5 bc', AstroDate(-4, 1, 1), AstroDate(-4, 4, 1)),
    ('the last weekend of june 5 bc', AstroDate(-4, 6, 29), AstroDate(-4, 7, 1)),
])
def test_small_bc_year_composes_beyond_calendar_date(text, start_, end_):
    """quarter_ref and weekend_of_month carry the same ERA slot."""
    assert start_end(text) == (start_, end_)
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text", ['31', '12', '5'])
def test_bare_small_number_is_still_not_a_year(text):
    """The >=32 floor stands wherever no era marker licenses it."""
    assert parse(text) is None


@pytest.mark.parametrize("text", ['march 15th, 31', 'march 15th, 12'])
def test_unmarked_small_number_is_still_not_a_year(text):
    """Without a marker the trailing numeral stays a stranded day-of-month
    candidate rather than quietly becoming a first-century year."""
    got, remainder = parse(text)
    assert got.start.year > 1000
    assert remainder == text.split()[-1]
