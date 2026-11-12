"""A day, weekday or week "of the month" that has passed is next month's, en.

A named occurrence is the next one after the anchor, and a span that ended
before the anchor names the next such span.  "of this month" names the
anchor's own month and never rolls.

Anchor Saturday 2026-10-17 12:00.  October 2026 starts on a Thursday (first
Tuesday the 6th); November 2026 starts on a Sunday (first Tuesday the 3rd,
first Monday the 2nd).  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,ymd", [
    ("the first tuesday of the month", (2026, 11, 3)),
    ("the first day of the month", (2026, 11, 1)),
    ("the first week of the month", (2026, 11, 2)),
    ("the last day of the month", (2026, 10, 31)),
    ("the first tuesday of this month", (2026, 10, 6)),
    ("the first day of this month", (2026, 10, 1)),
])
def test_of_the_month(text, ymd):
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


@pytest.mark.parametrize("text,anchor,ymd", [
    # The first week of October 2026 is Monday 5 to Monday 12 (exclusive):
    # said at midnight on the 12th it has ended, so it is November's, which
    # starts on Monday 2 November.
    ("the first week of the month", datetime(2026, 10, 12), (2026, 11, 2)),
    # 1 October has ended at midnight on 2 October.
    ("the first day of the month", datetime(2026, 10, 2), (2026, 11, 1)),
    # Said at noon on 1 October, the first day of the month is still today.
    ("the first day of the month", datetime(2026, 10, 1, 12), (2026, 10, 1)),
])
def test_a_span_that_ends_at_the_anchor_has_passed(text, anchor, ymd):
    span, rest = extract_timespan(text, "en", anchor)
    assert span.start == AstroDate(*ymd)
    assert rest == ""
