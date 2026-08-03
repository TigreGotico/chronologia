"""Wave 1 -- Gregorian calendar dates in every order and style.

A dated day is day-wide; a bare month (or month+year) is month-wide.  With
no explicit year the engine's ``prefer_future`` rolls a day already past on
the anchor day into next year -- but only when a day is named; a bare month
keeps the anchor year.  Impossible dates never parse.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, ad, start, start_end, span, nomatch

_ANCHOR_DAY = ANCHOR.date()


def _future_year(month, day):
    """Independent oracle for the no-year prefer_future roll."""
    return 2017 if date(2017, month, day) >= _ANCHOR_DAY else 2018


# -- day-dated, no year: prefer_future roll -------------------------------

_DAYCASES = [
    ("june fifth", 6, 5), ("june 5", 6, 5), ("june 30", 6, 30),
    ("july 4", 7, 4), ("january 1", 1, 1), ("december 25", 12, 25),
    ("the fifth of june", 6, 5), ("the 5th of june", 6, 5),
    ("june 1st", 6, 1), ("june 2nd", 6, 2), ("june 3rd", 6, 3),
    ("june 21st", 6, 21), ("june 22nd", 6, 22), ("june 27th", 6, 27),
    ("june 28th", 6, 28), ("may 5", 5, 5), ("august 15", 8, 15),
    ("march 3", 3, 3), ("october 31", 10, 31), ("november 11", 11, 11),
    ("the twenty first of june", 6, 21), ("june twenty fifth", 6, 25),
    ("jan 1", 1, 1), ("feb 14", 2, 14), ("sep 9", 9, 9), ("dec 31", 12, 31),
    ("the first of july", 7, 1), ("the thirty first of december", 12, 31),
]


@pytest.mark.parametrize("text,m,d", _DAYCASES)
def test_day_dated_no_year(text, m, d):
    y = _future_year(m, d)
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- day-dated, explicit year (no roll) -----------------------------------

_YEARCASES = [
    ("5th june 2027", 2027, 6, 5), ("june 5, 2027", 2027, 6, 5),
    ("5 june 2027", 2027, 6, 5), ("june 5 2027", 2027, 6, 5),
    ("the 5th of june 2027", 2027, 6, 5), ("dec 25 2020", 2020, 12, 25),
    ("january 1 2000", 2000, 1, 1), ("july 20 1969", 1969, 7, 20),
    ("february 29 2020", 2020, 2, 29), ("29 february 2020", 2020, 2, 29),
    ("october 12 1492", 1492, 10, 12), ("14 july 1789", 1789, 7, 14),
    ("september 11 2001", 2001, 9, 11), ("4 july 1776", 1776, 7, 4),
    ("november 9 1989", 1989, 11, 9), ("august 6 1945", 1945, 8, 6),
]


@pytest.mark.parametrize("text,y,m,d", _YEARCASES)
def test_day_dated_with_year(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- bare month (current year, month-wide, no roll) -----------------------

_MONTHNAMES = ["january", "february", "march", "april", "may", "june",
               "july", "august", "september", "october", "november",
               "december"]


@pytest.mark.parametrize("m,name", list(enumerate(_MONTHNAMES, 1)))
def test_bare_month(m, name):
    s, e = start_end(name)
    assert s == AstroDate(2017, m, 1)
    ny, nm = (2018, 1) if m == 12 else (2017, m + 1)
    assert e == AstroDate(ny, nm, 1)


# -- month + year (month-wide) --------------------------------------------

@pytest.mark.parametrize("text,y,m", [
    ("june 2027", 2027, 6), ("december 1999", 1999, 12),
    ("january 2000", 2000, 1), ("july 1969", 1969, 7),
    ("october 1929", 1929, 10), ("april 1912", 1912, 4),
])
def test_month_and_year(text, y, m):
    s, e = start_end(text)
    assert s == AstroDate(y, m, 1)
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    assert e == AstroDate(ny, nm, 1)


# -- ISO literals ---------------------------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("2027-06-05", 2027, 6, 5), ("2017-06-30", 2017, 6, 30),
    ("2000-01-01", 2000, 1, 1), ("1969-07-20", 1969, 7, 20),
    ("2020-02-29", 2020, 2, 29),
])
def test_iso_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)
    assert span(text).width == timedelta(days=1)


# -- impossible / non-existent dates must not parse -----------------------

@pytest.mark.parametrize("text,bad", [
    ("the 31st of june", (6, 31)), ("june 31", (6, 31)),
    ("february 30th", (2, 30)), ("february 30", (2, 30)),
    ("november 31", (11, 31)), ("april 31", (4, 31)),
    ("february 29 2019", (2, 29)), ("2019-02-29", (2, 29)),
    ("the 32nd of may", (5, 32)),
])
def test_impossible_day_never_selected(text, bad):
    """The impossible day is rejected; a bare-month fallback may still fire,
    but never the non-existent day itself."""
    from ._corpus import parse
    res = parse(text)
    if res is not None:
        s = res[0].start
        assert (s.month, s.day) != bad


@pytest.mark.parametrize("text", [
    "the 31st of june", "february 30th", "november 31", "february 29 2019",
    "2019-02-29",
])
def test_hard_impossible_no_match(text):
    nomatch(text)


# -- deferred: "the first of the month" / bare year -----------------------

# Nth of the current month (prefer_future rolls a passed day to next month)
@pytest.mark.parametrize("text,d", [
    ("the first of the month", AstroDate(2017, 7, 1)),
    ("the 28th of the month", AstroDate(2017, 6, 28)),   # still ahead of the 27th
    ("the 15th of the month", AstroDate(2017, 7, 15)),   # passed -> next month
])
def test_first_of_the_month(text, d):
    assert start(text) == d


# The prefer-future roll of "the Nth of the month" must land on the next month
# that actually HAS that day-of-month, not day-clamp: from a Jan-31 anchor, "by
# the 30th" (Jan 30 already passed) skips February (no 30th) to March 30 -- the
# old blind +1-month clamped it to Feb 28, silently relabelling the day.
@pytest.mark.parametrize("text,anchor,d", [
    ("by the 30th", datetime(2017, 1, 31, 13, 4), AstroDate(2017, 3, 30)),
    ("on the 29th", datetime(2017, 1, 31, 13, 4), AstroDate(2017, 3, 29)),  # 2017 Feb no 29
    ("by the 31st", datetime(2017, 4, 15, 13, 4), AstroDate(2017, 5, 31)),  # Apr no 31 -> May
])
def test_month_day_roll_skips_months_without_the_day(text, anchor, d):
    assert start(text, anchor) == d


# -- "on/by the Nth": preposition-signalled bare day-of-month -------------
#
# A leading date preposition ("on"/"by") makes a bare *digit* ordinal a
# day-of-month: the Nth of the anchor's current month, prefer_future rolling
# a day already past into next month.  Anchor is Tuesday 2017-06-27, so the
# 28th/30th are still ahead this June and the 3rd/5th/15th have passed.
@pytest.mark.parametrize("text,d", [
    ("on the 28th", AstroDate(2017, 6, 28)),    # still ahead of the 27th
    ("on the 30th", AstroDate(2017, 6, 30)),
    ("on the 3rd", AstroDate(2017, 7, 3)),      # passed -> next month
    ("on the 5th", AstroDate(2017, 7, 5)),
    ("on the 15th", AstroDate(2017, 7, 15)),
    ("by the 28th", AstroDate(2017, 6, 28)),
    ("by the 5th", AstroDate(2017, 7, 5)),      # "by monday" semantics: prefer_future
    ("meet me on the 29th", AstroDate(2017, 6, 29)),
])
def test_on_the_nth_day_of_month(text, d):
    s, e = start_end(text)
    assert s == d
    assert e == d + timedelta(days=1)           # a day-wide span


# adversarial: bare digit ordinals are a day-of-month ONLY behind an "on"/"by"
# signal.  Truly bare "the Nth" stays an honest, unresolved boundary (never a
# silent-wrong date) -- resolving it risks the ordinal homograph trap.
@pytest.mark.parametrize("text", [
    "the 15th", "the 25th", "the 3rd", "the 5th",
])
def test_bare_nth_without_preposition_does_not_bind(text):
    nomatch(text)


# -- bare / marked calendar year (year-wide span) -------------------------

@pytest.mark.parametrize("text,year", [
    ("2027", 2027), ("in 1995", 1995), ("the year 2000", 2000),
    ("year 1969", 1969), ("in 1492", 1492), ("2020", 2020),
    ("the year 1000", 1000),
])
def test_bare_year(text, year):
    s, e = start_end(text)
    assert s == AstroDate(year, 1, 1)
    assert e == AstroDate(year + 1, 1, 1)


# adversarial: a small integer is NOT a year (needs 4 digits / >= 32).
@pytest.mark.parametrize("text,n", [("3", 3), ("12", 12), ("in 5", 5)])
def test_small_int_is_not_a_year(text, n):
    from ._corpus import parse
    r = parse(text)
    assert r is None or r[0].start.year != n
