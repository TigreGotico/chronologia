# -*- coding: utf-8 -*-
"""\"the last week of 2026\" is the last ISO 8601 week of 2026, en.

The last ISO week of a year is the week for which Wikipedia ("ISO week
date") gives "It has 28 December in it".  28 December 2026 is a Monday, so
the week runs from 28 December 2026 to 3 January 2027.  28 December 2020 is
a Monday too, and 2020 has 53 weeks.  28 December 2025 is a Sunday, so the
last week of 2025 starts on Monday 22 December.  1 January 2026 is a
Thursday, so week 01 of 2026 starts on Monday 29 December 2025 (Wikipedia:
week 01 is "the week with the first Thursday of the Gregorian year").
Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,begin,end", [
    ("the last week of 2026", (2026, 12, 28), (2027, 1, 4)),
    ("the last week of 2020", (2020, 12, 28), (2021, 1, 4)),
    ("the last week of last year", (2025, 12, 22), (2025, 12, 29)),
    ("the first week of the year", (2025, 12, 29), (2026, 1, 5)),
    ("the first week of this year", (2025, 12, 29), (2026, 1, 5)),
])
def test_last_week_of_year(text, begin, end):
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""


def test_last_week_without_a_year_is_the_previous_week():
    # "last week" said on Saturday 17 October 2026 is Monday 5 to Monday 12.
    span, rest = extract_timespan("last week", "en", SATURDAY)
    assert (span.start, span.end) == (AstroDate(2026, 10, 5),
                                      AstroDate(2026, 10, 12))


# A count of weeks or a plural week noun names no one ISO week: "two weeks
# of 2026" is two weeks, not week 02.  The phrase refuses or keeps words in
# the remainder.
@pytest.mark.parametrize("text", [
    "two weeks of 2026",
    "one week of 2026",
    "the first weeks of 2026",
    "the last weeks of 2026",
])
def test_a_count_of_weeks_is_not_an_iso_week(text):
    r = extract_timespan(text, "en", SATURDAY)
    assert r is None or r.remainder != "", (
        f"{text!r} read {r!r} with nothing left over")
