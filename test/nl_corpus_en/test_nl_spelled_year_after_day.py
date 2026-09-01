# -*- coding: utf-8 -*-
"""A spelled year pair spoken after a spelled day-of-month.

"september first, twenty twenty six" names one date and one date only.  The
spelled pair used to reach the matcher as a plain cardinal run glued to the
ordinal day, so the day was silently overwritten by the pair's tail (Sep 26
for Sep 1) while the remainder stayed empty -- a confidently wrong answer with
nothing to signal it.  Every case here therefore pins the remainder as well as
the span.

Expected values are plain calendar arithmetic: an explicit month, day and year
name exactly that day, and a day-wide span runs 00:00 to 00:00 the next
morning.  The anchor is 2026-09-01, a Tuesday, chosen so a mis-read pair lands
in a visibly different year.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, parse

ANCHOR = datetime(2026, 9, 1)


def _one(text):
    r = parse(text, ANCHOR)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    span, remainder = r
    assert remainder == "", f"{text!r} left remainder {remainder!r}"
    return span


# -- the defect: both halves spelled --------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("september first, twenty twenty six", 2026, 9, 1),
    ("july fourth nineteen seventy six", 1976, 7, 4),
    ("september tenth nineteen eighty four", 1984, 9, 10),
    ("march third twenty twenty five", 2025, 3, 3),
    ("december thirty first twenty twenty", 2020, 12, 31),
])
def test_spelled_day_and_spelled_year(text, y, m, d):
    span = _one(text)
    assert span.start == AstroDate(y, m, d)
    assert span.width == timedelta(days=1)


def test_weekday_prefix_and_clock_keep_the_spelled_day():
    span = _one("tuesday, september first, twenty twenty six at three o'clock")
    assert span.start == AstroDate(2026, 9, 1, 3, 0)


# -- controls: the digit spellings that always worked ---------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("july fourth 1976", 1976, 7, 4),
    ("july 4th nineteen seventy six", 1976, 7, 4),
    ("september first, 2026", 2026, 9, 1),
])
def test_digit_forms_unchanged(text, y, m, d):
    assert _one(text).start == AstroDate(y, m, d)


# -- controls: a spelled year with no day ---------------------------------

@pytest.mark.parametrize("text", ["in nineteen eighty four",
                                  "the year nineteen eighty four"])
def test_cued_spelled_year_alone(text):
    span = _one(text)
    assert span.start == AstroDate(1984, 1, 1)
    assert span.end == AstroDate(1985, 1, 1)


# -- control: a spelled day with no year ----------------------------------

def test_spelled_day_without_year_stays_anchor_relative():
    # Sep 1 is the anchor day itself, so prefer_future keeps 2026.
    span = _one("september first")
    assert span.start == AstroDate(2026, 9, 1)
    assert span.width == timedelta(days=1)


# -- refusals held: an uncued bare pair is still not a date ---------------
#
# Without a cue word or a preceding month+day, "twenty twenty" is as much a
# count as a year; the engine refuses rather than guessing, and licensing the
# date-head context must not turn that refusal into a confident answer.

@pytest.mark.parametrize("text", ["twenty twenty", "nineteen ninety nine",
                                  "twenty twenty six", "nineteen eighty four"])
def test_bare_spelled_pair_still_refused(text):
    assert parse(text, ANCHOR) is None


# -- the counting reading of the same words survives ----------------------

def test_spelled_count_offset_is_not_a_year():
    span = _one("in twenty five days")
    assert span.start == AstroDate(2026, 9, 26)
