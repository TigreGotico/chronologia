# -*- coding: utf-8 -*-
"""A "tonight" in a later clause does not replace the date of the first clause.

Anchor Tuesday 2017-06-27 13:04.  "in a day" is the anchor plus one day,
"in two days" the anchor plus two days, "tomorrow" the next calendar day.
A word "to" before the date must not open a range whose left side is only
the borrowed "tonight".  Issue: https://github.com/TigreGotico/chronologia/issues/1433
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

TUE = datetime(2017, 6, 27, 13, 4)

# text, expected start
FIRST_CLAUSE = [
    ("Our neighbor's moving truck is supposed to arrive in a day, so we'd "
     "better finish packing the spare room tonight.", TUE + timedelta(days=1)),
    ("The truck is supposed to come tomorrow, so we pack tonight.",
     datetime(2017, 6, 28)),
    ("The painters are due to start in two days; tonight we pack.",
     TUE + timedelta(days=2)),
    ("The painters are due to start in two days, so we pack tonight.",
     TUE + timedelta(days=2)),
    ("My sister is going to visit in a day, so I clean the house tonight.",
     TUE + timedelta(days=1)),
]

# "tonight" is the only date: the evening of the anchor day
ONLY_TONIGHT = [
    "We are supposed to finish packing tonight.",
    "I have to call my mother tonight.",
    "Remember to water the plants tonight.",
]


@pytest.mark.parametrize("text,expected", FIRST_CLAUSE)
def test_first_clause_date_wins(text, expected):
    got = extract_timespan(text, "en", TUE)
    assert got.span.start.datetime() == expected


@pytest.mark.parametrize("text", ONLY_TONIGHT)
def test_tonight_alone_is_this_evening(text):
    start = extract_timespan(text, "en", TUE).span.start.datetime()
    assert start.date() == TUE.date() and start.hour >= 18
    assert "tonight" not in extract_timespan(text, "en", TUE).remainder
