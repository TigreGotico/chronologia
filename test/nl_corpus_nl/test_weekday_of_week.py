# -*- coding: utf-8 -*-
"""A weekday of a relative week (Dutch): the named day of the shifted week.

"<weekday> of next week" and "next week <weekday>" name a day inside the
shifted Monday-start week, not the bare weekday's next occurrence.  Every
anchor weekday is tried, because from a Saturday the two readings coincide
and hide the difference.  Expected days come from ``datetime.date``
arithmetic on the anchor, never from the parser.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import parse

CASES = [('vrijdag van volgende week', 4, 1), ('volgende week vrijdag', 4, 1), ('vrijdag van vorige week', 4, -1), ('vorige week maandag', 0, -1), ('zondag van volgende week', 6, 1)]

# Monday 2026-10-19 and the six days after it.
ANCHORS = [datetime(2026, 10, 19 + i, 10, 0) for i in range(7)]


def _day(anchor, weekday, weeks):
    monday = anchor.date() - timedelta(days=anchor.weekday())
    return monday + timedelta(weeks=weeks, days=weekday)


@pytest.mark.parametrize("anchor", ANCHORS, ids=lambda a: a.strftime("%a"))
@pytest.mark.parametrize("text,weekday,weeks", CASES)
def test_weekday_of_relative_week(text, weekday, weeks, anchor):
    span, remainder = parse(text, anchor)
    want = _day(anchor, weekday, weeks)
    assert (span.start.year, span.start.month, span.start.day) == (
        want.year, want.month, want.day)
    assert (span.end - span.start).days == 1
    assert remainder == ""
