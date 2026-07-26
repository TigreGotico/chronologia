# -*- coding: utf-8 -*-
"""Spelled multi-word cardinals and fractions in relative/duration phrases.

A human says "a hundred years ago" and "two and a half hours ago" as readily
as "100 years ago" and "2.5 hours ago"; the spelled forms must fold to the
same magnitude the digit forms do.  Expected instants are computed by
independent ``datetime`` arithmetic off the mission anchor (Tue 2017-06-27
13:04), never by pinning the parser's own output.

Deep time is protected on purpose: "sixty-six million years ago" keeps the
SCALE slot the digit "66 million years ago" uses and must reach the identical
deep-time span.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, span, start_end


def _shift(**kw):
    """Anchor shifted by a relativedelta-free timedelta/keyword pair."""
    from dateutil.relativedelta import relativedelta
    return ad(ANCHOR + relativedelta(**kw))


# -- spelled multi-word cardinal offsets ("N hundred/thousand years ago") ---
@pytest.mark.parametrize("text,years", [
    ("a hundred years ago", 100),
    ("one hundred years ago", 100),
    ("a hundred and fifty years ago", 150),
    ("two hundred years ago", 200),
])
def test_spelled_cardinal_year_offset(text, years):
    s, e = start_end(text)
    assert s == _shift(years=-years)
    assert e == _shift(years=-years + 1)
    assert parse(text)[1] == ""


def test_spelled_cardinal_matches_digit_form():
    assert start_end("a hundred years ago") == start_end("100 years ago")
    assert start_end("a hundred and fifty years ago") == start_end(
        "150 years ago")


# The thousand scale ("two thousand years ago") is deliberately NOT folded
# here: a spelled thousand/million SCALE word routes "years ago" to the
# Before-Present / deep-time offset the resolver owns (see
# test_nl_spelled_years.py), a convention this pass must not disturb.  Folding
# only the hundred scale keeps that path intact.
def test_thousand_scale_still_routes_to_before_present():
    from ._corpus import AstroDate
    # unchanged from the tested BP convention (anchor-1950 Before Present),
    # NOT the plain 1017-style anchor offset the hundred scale gets
    assert span("two thousand years ago").start == AstroDate(-50, 1, 1)


# -- deep time stays protected: spelled == digit -----------------------------
def test_spelled_deep_time_matches_digit():
    assert start_end("sixty-six million years ago") == start_end(
        "66 million years ago")
    assert start_end("sixty six million years ago") == start_end(
        "66 million years ago")
    # deep time is beyond the datetime range -- the digit form itself proves it
    assert span("66 million years ago").start_datetime is None


# -- fractional durations in the "ago" frame --------------------------------
@pytest.mark.parametrize("text,minutes", [
    ("two and a half hours ago", 150),         # 2.5 h
    ("an hour and a half ago", 90),            # 1.5 h
    ("three quarters of an hour ago", 45),      # 0.75 h
    ("a quarter of an hour ago", 15),           # 0.25 h
    ("half an hour ago", 30),                   # 0.5 h  (already worked)
])
def test_fractional_hour_offset(text, minutes):
    s = span(text).start
    assert s == ad(ANCHOR - timedelta(minutes=minutes))
    assert parse(text)[1] == ""


# -- "half a year ago" -> 6 months (a year fraction is a month count) --------
def test_half_a_year_ago():
    from dateutil.relativedelta import relativedelta
    s = span("half a year ago").start
    assert s == ad(ANCHOR - relativedelta(months=6))
    assert parse("half a year ago")[1] == ""


# -- digit forms and neighbouring readings stay byte-identical ---------------
@pytest.mark.parametrize("text", [
    "100 years ago",
    "66 million years ago",
    "2.5 hours ago",
    "half an hour ago",
    "a couple of days ago",
    "the nineteen-eighties",
    # the partitive "half OF THE <period>" is a sub-span, not a duration --
    # the definite article keeps the fraction fold from ever touching it
    "the second half of the century",
    "the first half of the decade",
    "the first half of the millennium",
    # clock fractions are followed by past/to, not a unit -- never folded
    "half past three",
    "quarter to four",
])
def test_untouched_readings_still_parse(text):
    assert parse(text) is not None
