# -*- coding: utf-8 -*-
"""Composition-correctness regressions: the four wrong outputs an architecture
audit of the token-native pipeline turned up, each fixed and pinned here with a
hand-derived expected value.

Anchor is **Wednesday 2026-07-22** unless a test says otherwise.  July 2026
(July 1 is a Wednesday)::

    Mon  6 13 20 27      Thu  2  9 16 23 30
    Tue  7 14 21 28      Fri  3 10 17 24 31
    Wed  1  8 15 22 29   Sat  4 11 18 25
                         Sun  5 12 19 26

Business days after Wed 22 (weekday-only, no US holiday in range):
    Thu23(1) Fri24(2) Mon27(3) Tue28(4) Wed29(5)
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 7, 22)      # Wednesday


def _parse(text, **kw):
    r = extract_timespan(text, "en", ANCHOR, **kw)
    assert r is not None, f"{text!r} did not parse"
    return r


# -- BUG 1: a trailing clock composes onto a business-day count ------------
# "in 5 business days at 3pm" used to drop the 3pm (business-day output was not
# in the composable-date set), stranding "in at 3pm" in the remainder.

def test_business_days_compose_with_trailing_clock():
    span, remainder = _parse("in 5 business days at 3pm", jurisdiction="US")
    # 5th US business day after Wed 22 == Wed 29, at 15:00 (minute-wide)
    assert span.start == AstroDate(2026, 7, 29, 15, 0)
    assert span.end == AstroDate(2026, 7, 29, 15, 1)
    assert remainder == ""


def test_business_days_bare_count_still_day_wide():
    # without a clock the count is a whole-day span, and "in" is consumed
    span, remainder = _parse("in 5 business days", jurisdiction="US")
    assert span.start == AstroDate(2026, 7, 29)
    assert span.end == AstroDate(2026, 7, 30)
    assert remainder == ""


def test_anchored_offset_composes_with_trailing_clock():
    # the parallel path (offset-after a holiday) already composed; pin it so it
    # cannot regress alongside the business-day fix.  Christmas 2026 is Fri 25;
    # 3 days after == Mon 28, at noon.
    span, _ = _parse("3 days after christmas at noon")
    assert span.start == AstroDate(2026, 12, 28, 12, 0)
    assert span.end == AstroDate(2026, 12, 28, 12, 1)


# -- BUG 2: "since X" is past-anchored, not prefer_future ------------------
# "since july 6" used to fling the near-past date a year forward (2027) and
# drop the "since" marker.  It must resolve to the most recent past occurrence.

def test_since_recent_month_day_is_past_anchored():
    span, remainder = _parse("since july 6")
    assert span.start == AstroDate(2026, 7, 6)      # this year, already passed
    assert span.end == AstroDate(2026, 7, 22)       # the anchor instant
    assert remainder == ""                          # "since" consumed


def test_since_explicit_year_unchanged():
    span, _ = _parse("since 2019")
    assert span.start == AstroDate(2019, 1, 1)
    assert span.end == AstroDate(2026, 7, 22)


def test_since_bare_month_resolves_to_last_occurrence():
    # December is in the future of a July anchor, so "since december" means
    # *last* December (2025), not the coming one.
    span, _ = _parse("since december")
    assert span.start == AstroDate(2025, 12, 1)
    assert span.end == AstroDate(2026, 7, 22)


# -- BUG 3: "week of" inside a range -- a date-to-date range whose start is
# week-widened.  Both endpoints (July 6, July 20) sit just behind the July 22
# anchor, so prefer_future applies *consistently* to both and the whole range
# reads in the next cycle (2027) -- the established range convention (see
# test_nl_ranges: "from june 1 to june 10" -> next year).  The point of the
# regression is that the year is STABLE and CONSISTENT: the week-widened start
# and the end land in the same year, never one leaping past the other.

def test_week_of_to_date_range_is_year_consistent():
    span, remainder = _parse("the week of july 6 to july 20")
    # start = monday-of-the-week-containing July 6 2027 (Tue) == Mon July 5 2027
    assert span.start == AstroDate(2027, 7, 5)
    # end = the day after July 20 2027
    assert span.end == AstroDate(2027, 7, 21)
    assert span.start.year == span.end.year          # no year leak across ends
    assert remainder == ""


# -- BUG 4: a reversed / inconsistent range never fabricates a span --------
# The roll-forward used to advance a fixed calendar date by single days,
# fabricating a bogus tiny span from a genuinely reversed range.  A range whose
# endpoints cannot form an ordered span must fall through to a clean single-span
# partial (or None), never invent one.

@pytest.mark.parametrize("text,keep", [
    # reversed, both years pinned -> range refuses; the left date is the partial
    ("from june 12 2020 to june 5 2020", AstroDate(2020, 6, 12)),
    ("from june 5 2020 to june 5 2019", AstroDate(2020, 6, 5)),
])
def test_reversed_pinned_range_does_not_fabricate(text, keep):
    span, remainder = _parse(text)
    # a single day-wide date, NOT a fabricated multi-part span
    assert span.start == keep
    assert (span.end - span.start).days == 1
    assert remainder != ""                           # the rest is leftover text


def test_unparseable_right_endpoint_falls_through_cleanly():
    span, remainder = _parse("from july 20 to xyzzy")
    assert (span.end - span.start).days == 1         # just "july 20"
    assert "xyzzy" in remainder


def test_forward_ordered_range_still_composes():
    # the fix must not disturb an ordinary ordered range
    span, _ = _parse("from july 20 to august 5")
    assert span.start == AstroDate(2026, 7, 20)
    assert span.end == AstroDate(2026, 8, 6)
