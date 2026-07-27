"""Anchored arithmetic (feature 1): an offset applied to a resolved reference.

"two weeks after easter", "3 days before christmas", "the monday after
christmas", "the friday before easter" -- a signed unit offset or a strict
weekday roll composed onto ANY date-resolving submatch (holiday, calendar
date, weekday ref).  The reference is resolved first, then the offset is
applied to its span; nothing is re-parsed.

Anchor is 2017-06-27 (a Tuesday, 13:04).  Reference dates are hand-derived
from the independent Western computus / civil-calendar table used by
``test_nl_holiday_ref`` (bare = next occurrence on/after the anchor):

    easter 2018 = Sun 2018-04-01   good friday 2018 = 2018-03-30
    christmas   = Mon 2017-12-25   new year's day   = 2018-01-01
    july 4th    = 2017-07-04       next friday      = 2017-06-30
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, span, start, nomatch

EASTER = date(2018, 4, 1)
GOOD_FRIDAY = date(2018, 3, 30)
CHRISTMAS = date(2017, 12, 25)
NEW_YEAR = date(2018, 1, 1)
JULY4 = date(2017, 7, 4)
NEXT_FRIDAY = date(2017, 6, 30)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


# -- signed unit offset from a holiday/date reference ---------------------

@pytest.mark.parametrize("text,expected", [
    ("2 weeks after easter", EASTER + timedelta(days=14)),
    ("two weeks after easter", EASTER + timedelta(days=14)),
    ("1 week after easter", EASTER + timedelta(days=7)),
    ("a week after easter", EASTER + timedelta(days=7)),
    ("the week after easter", EASTER + timedelta(days=7)),
    ("3 days before christmas", CHRISTMAS - timedelta(days=3)),
    ("10 days after christmas", CHRISTMAS + timedelta(days=10)),
    ("the day after christmas", CHRISTMAS + timedelta(days=1)),
    ("the day before easter", EASTER - timedelta(days=1)),
    ("2 weeks after good friday", GOOD_FRIDAY + timedelta(days=14)),
    ("a week before new year's day", NEW_YEAR - timedelta(days=7)),
    ("3 days after july 4th", JULY4 + timedelta(days=3)),
    ("2 days before july 4th", JULY4 - timedelta(days=2)),
    ("two weeks after next friday", NEXT_FRIDAY + timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("1 month after easter", date(2018, 5, 1)),
    ("2 months before christmas", date(2017, 10, 25)),
])
def test_month_offset(text, expected):
    assert start(text) == _ad(expected)


# -- strict weekday roll relative to the reference ------------------------
# christmas 2017-12-25 is a Monday; easter 2018-04-01 is a Sunday.

@pytest.mark.parametrize("text,expected", [
    ("the monday after christmas", date(2018, 1, 1)),   # +7, strictly after
    ("the friday after christmas", date(2017, 12, 29)),
    ("the tuesday before christmas", date(2017, 12, 19)),
    ("the friday before easter", date(2018, 3, 30)),
    ("the sunday after easter", date(2018, 4, 8)),      # +7, strictly after
    ("the saturday before easter", date(2018, 3, 31)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# -- referential width: an offset resolves to the single shifted day ------
# The offset amount governs the SHIFT, never the result width: "2 weeks after
# easter" is the single civil day 14 days after easter, not a 14-day span.
# (Previously this asserted a week-wide span -- that was the silent-wrong; see
# test_nl_anchored_offset_point.)

def test_week_offset_is_day_wide():
    assert span("2 weeks after easter").width == timedelta(days=1)


def test_day_offset_is_day_wide():
    assert span("3 days before christmas").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("the monday after christmas").width == timedelta(days=1)


# -- negatives / confusables: existing behaviour must be preserved ---------

def test_bare_after_holiday_unchanged():
    # "after easter" with no offset pre-amble is the existing holiday_ref
    # behaviour: the holiday itself, not a shifted date.
    assert start("after easter") == _ad(EASTER)


@pytest.mark.parametrize("text,days", [
    ("the day after tomorrow", 2),      # named_day_after idiom, NOT composed
    ("day after tomorrow", 2),
    ("the day before yesterday", -2),
])
def test_named_day_idioms_unchanged(text, days):
    from ._corpus import ANCHOR
    exp = (ANCHOR + timedelta(days=days)).replace(hour=0, minute=0)
    assert start(text) == AstroDate(exp.year, exp.month, exp.day)


@pytest.mark.parametrize("text", [
    "3 days before the deadline",       # "the deadline" is not a resolved ref
    "the day after the wedding",
    "2 weeks after the meeting",
])
def test_no_reference_no_offset(text):
    nomatch(text)
