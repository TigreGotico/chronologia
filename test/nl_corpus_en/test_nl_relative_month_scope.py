"""Relative-month scope of nth-weekday / day-of-month / business-day
constructions.

A named-month scope binds cleanly ("third Wednesday of March"), but the
RELATIVE-month scope of the same constructions ("... of the month", "... of
next month") used to strand the scope words and silently return a
wrong (anchor-month or anchor-relative) date.  These pins assert the exact
resolved date for the relative-month surface, with the named-month cases kept
as byte-identical regression pins.

Anchor is 2017-06-27 (a Tuesday, 13:04).  Expected values come from
independent Python arithmetic, never from the parser.
"""
import pytest

from ._corpus import AstroDate, start


# -- nth weekday of a RELATIVE month --------------------------------------

@pytest.mark.parametrize("text,expected", [
    # "the month" / "this month" == the anchor's own month (June 2017)
    ("third Wednesday of the month", AstroDate(2017, 6, 21)),
    ("the third Wednesday of this month", AstroDate(2017, 6, 21)),
    # "next month" == anchor month + 1 (July 2017)
    ("the second Monday of next month", AstroDate(2017, 7, 10)),
    ("the second Tuesday of next month", AstroDate(2017, 7, 11)),
    # "last month" == anchor month - 1 (May 2017): 1st Fri of May = May 5
    ("the first Friday of last month", AstroDate(2017, 5, 5)),
])
def test_nth_weekday_relative_month(text, expected):
    assert start(text) == expected


# -- day-of-month of a RELATIVE month -------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("the 15th of next month", AstroDate(2017, 7, 15)),
    ("the 20th day of next month", AstroDate(2017, 7, 20)),
])
def test_day_of_relative_month(text, expected):
    assert start(text) == expected


# -- business day of a RELATIVE month -------------------------------------

@pytest.mark.parametrize("text,expected", [
    # Jul 1 is Sat, Jul 2 Sun -> 1st business day of July = Jul 3 (Mon)
    ("the first business day of next month", AstroDate(2017, 7, 3)),
])
def test_business_day_relative_month(text, expected):
    assert start(text) == expected


# -- CONTRAST: named-month scope must stay byte-identical ------------------

@pytest.mark.parametrize("text,expected", [
    ("third Wednesday of March", AstroDate(2017, 3, 15)),
    ("third Wednesday of June", AstroDate(2017, 6, 21)),
])
def test_named_month_scope_unchanged(text, expected):
    assert start(text) == expected
