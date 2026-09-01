"""A week-scale construction on a BC date must not fall back to ``datetime``.

``AstroDate`` is unbounded, so "january 1st, 300 bc" resolves to the
astronomical year -299, but the week widening built a ``datetime`` from that
year purely to read its weekday -- and ``datetime`` refuses any year below 1.
Every week-scale phrase anchored before year one therefore raised
``ValueError: year -299 is out of range`` out of the middle of the parse
instead of returning a span.

Gold is computed from the proleptic Gregorian Julian Day Number, independently
of both the parser and ``datetime``: with JDN mod 7 == 0 on a Monday,
1 January -299 is JDN 1611853, and 1611853 mod 7 == 5 == Saturday, so the
Monday-start week containing it begins five days earlier on 27 December -300
(JDN 1611848, mod 7 == 0 == Monday) and ends seven days after that. Likewise
15 March -43 is JDN 1705428, mod 7 == 4 == Friday, whose week begins on
Monday 11 March -43 (JDN 1705424).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

_ANCHOR = datetime(2026, 9, 1)


def _span(text):
    result = extract_timespan(text, "en-us", anchor=_ANCHOR)
    assert result is not None, text
    assert result.remainder == "", result.remainder
    return result.span


@pytest.mark.parametrize("text, start, end", [
    ("the week of january 1st, 300 bc",
     AstroDate(-300, 12, 27), AstroDate(-299, 1, 3)),
    ("the week of march 15th, 44 bc",
     AstroDate(-43, 3, 11), AstroDate(-43, 3, 18)),
])
def test_the_week_of_a_bc_date_spans_its_calendar_week(text, start, end):
    span = _span(text)
    assert span.start == start
    assert span.end == end


def test_the_week_after_a_bc_date_moves_a_week_on():
    span = _span("the week after january 1st, 300 bc")
    assert span.start == AstroDate(-299, 1, 3)
    assert span.end == AstroDate(-299, 1, 10)


@pytest.mark.parametrize("text, start", [
    ("the week of january 1st, 300 ad", AstroDate(300, 1, 1)),
    ("the week of september 1st, 2026", AstroDate(2026, 8, 31)),
])
def test_ad_weeks_are_unchanged(text, start):
    assert _span(text).start == start
