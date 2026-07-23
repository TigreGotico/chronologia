"""Composed reference dates whose qualifier words used to be silently
dropped, returning a confident wrong subset.  Each phrase must now *compose*
so every word is consumed.

Anchor: Wednesday 2024-03-06 12:00.  Expected values are hand-derived by
independent calendar arithmetic, never pinned from the engine.

Citations:
* "the last/first day of the month/year" -- ordinary English extremal-day
  reference relative to the current calendar period.
* "a week today" / "a week tomorrow" / "a fortnight today" -- British/Irish
  idiom, "N time-unit from [today/tomorrow]" = +N units.  Cambridge Dictionary
  ("a week today"): "a week from the day it is now".  Collins likewise.
* "a month from tomorrow" / "N units from today" -- American English "N units
  from <named day>" mirroring the already-supported "3 weeks from monday".
* "this time last year" / "this time next week" -- the anchor's same instant
  shifted by the named period.
* "the eve of <holiday>" -- the day before a named holiday (Christmas Eve is
  the eve of Christmas).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate


ANCHOR = datetime(2024, 3, 6, 12, 0)          # a Wednesday, noon


def start(text):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start


def remainder(text):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


# -- (A) extremal day of the current month/year ---------------------------

@pytest.mark.parametrize("text,expected", [
    ("the last day of the month", AstroDate(2024, 3, 31)),
    ("the first day of the month", AstroDate(2024, 3, 1)),
    ("the last day of the year", AstroDate(2024, 12, 31)),
    ("the first day of the year", AstroDate(2024, 1, 1)),
    ("the last day of this month", AstroDate(2024, 3, 31)),
    ("the first day of this month", AstroDate(2024, 3, 1)),
    ("the last day of next month", AstroDate(2024, 4, 30)),
    ("the first day of next month", AstroDate(2024, 4, 1)),
    ("the last day of last month", AstroDate(2024, 2, 29)),
    ("the last day of next year", AstroDate(2025, 12, 31)),
])
def test_extremal_day_of_period(text, expected):
    assert start(text) == expected
    assert remainder(text) == ""


# -- (B) "a week today" British idiom (+N units onto today/tomorrow) ------

@pytest.mark.parametrize("text,expected", [
    ("a week today", AstroDate(2024, 3, 13)),
    ("a week tomorrow", AstroDate(2024, 3, 14)),
    ("a fortnight today", AstroDate(2024, 3, 20)),
    ("a fortnight tomorrow", AstroDate(2024, 3, 21)),
    ("two weeks today", AstroDate(2024, 3, 20)),
    ("two weeks tomorrow", AstroDate(2024, 3, 21)),
])
def test_week_today_idiom(text, expected):
    assert start(text) == expected
    assert remainder(text) == ""


# -- (C) "N units from <named day>" ---------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("a month from tomorrow", AstroDate(2024, 4, 7)),
    ("a week from tomorrow", AstroDate(2024, 3, 14)),
    ("a week from today", AstroDate(2024, 3, 13)),
    ("two months from today", AstroDate(2024, 5, 6)),
    ("a year from today", AstroDate(2025, 3, 6)),
    ("three days from tomorrow", AstroDate(2024, 3, 10)),
])
def test_units_from_named_day(text, expected):
    assert start(text) == expected
    assert remainder(text) == ""


# -- (D) "this time <period-offset>" (same clock, shifted period) ---------

@pytest.mark.parametrize("text,expected", [
    ("this time last year", AstroDate(2023, 3, 6, 12, 0)),
    ("this time next year", AstroDate(2025, 3, 6, 12, 0)),
    ("this time next week", AstroDate(2024, 3, 13, 12, 0)),
    ("this time last week", AstroDate(2024, 2, 28, 12, 0)),
    ("this time tomorrow", AstroDate(2024, 3, 7, 12, 0)),
    ("this time yesterday", AstroDate(2024, 3, 5, 12, 0)),
    ("this time next month", AstroDate(2024, 4, 6, 12, 0)),
])
def test_this_time_shift(text, expected):
    assert start(text) == expected
    assert remainder(text) == ""


# -- (E) "the eve of <holiday>" -------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("the eve of christmas", AstroDate(2024, 12, 24)),
    ("eve of christmas", AstroDate(2024, 12, 24)),
])
def test_eve_of_holiday(text, expected):
    assert start(text) == expected
    assert remainder(text) == ""


# -- adversarial: the analogous already-working forms must NOT regress ----

@pytest.mark.parametrize("text,expected", [
    ("the last day of april", AstroDate(2024, 4, 30)),
    ("christmas eve", AstroDate(2024, 12, 24)),
    ("3 weeks from monday", AstroDate(2024, 4, 1)),
    ("today", AstroDate(2024, 3, 6)),
    ("tomorrow", AstroDate(2024, 3, 7)),
    ("next month", AstroDate(2024, 4, 1)),
    ("this month", AstroDate(2024, 3, 1)),
])
def test_no_regression_on_analogous_forms(text, expected):
    assert start(text) == expected


def test_this_year_unchanged():
    r = extract_timespan("this year", "en", ANCHOR)
    assert r is not None
    assert r[0].start == AstroDate(2024, 1, 1)
    assert r[0].end == AstroDate(2025, 1, 1)
