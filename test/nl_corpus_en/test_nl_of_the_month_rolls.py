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


@pytest.mark.parametrize("text,anchor,ymd", [
    # A weekday said on that day is the anchor's day (a day is a span, and
    # the span that holds the anchor is the current one): the first Tuesday
    # of October 2026 is the 6th, so at noon on Tuesday 6 October it is
    # today.  On Wednesday the 7th it has passed, and November's first
    # Tuesday is the 3rd.  The last Friday of October 2026 is the 30th.
    ("the first tuesday of the month", datetime(2026, 10, 6, 12),
     (2026, 10, 6)),
    ("the first tuesday of the month", datetime(2026, 10, 7, 12),
     (2026, 11, 3)),
    ("the last friday of the month", datetime(2026, 10, 30, 12),
     (2026, 10, 30)),
])
def test_a_weekday_said_on_that_day_is_today(text, anchor, ymd):
    span, rest = extract_timespan(text, "en", anchor)
    assert span.start == AstroDate(*ymd)
    assert rest == ""


# A "since" endpoint and the left end of a range ending today name a past
# start: the latest such day at or before the anchor, never next month's.
# The bare phrase rolls (ruling 13); the endpoint steps back one month at a
# time and counts the day in its own month.  On Saturday 17 October 2026 the
# first Tuesday of October is the 6th and the first day the 1st.  On
# Thursday 10 December 2026 the first day of December is the 1st, and
# 1 December 2026 is a Tuesday, so it is also the first Tuesday.
SAT17 = datetime(2026, 10, 17, 12, 0)
THU10 = datetime(2026, 12, 10, 10, 0)


@pytest.mark.parametrize("lang,text,anchor,begin,end", [
    ("en", "since the first tuesday of the month", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("en", "since the first day of the month", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("pt", "desde a primeira terça-feira do mês", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("pt", "desde o primeiro dia do mês", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("es", "desde el primer martes del mes", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("es", "desde el primer día del mes", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("fr", "depuis le premier mardi du mois", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("fr", "depuis le premier jour du mois", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("de", "seit dem ersten Dienstag des Monats", SAT17,
     (2026, 10, 6), (2026, 10, 17, 12)),
    ("de", "seit dem ersten Tag des Monats", SAT17,
     (2026, 10, 1), (2026, 10, 17, 12)),
    ("en", "from the first day of the month to today", SAT17,
     (2026, 10, 1), (2026, 10, 18)),
    ("en", "from the first day of the month to today", THU10,
     (2026, 12, 1), (2026, 12, 11)),
    ("en", "from the first tuesday of the month to today", THU10,
     (2026, 12, 1), (2026, 12, 11)),
    ("pt", "do primeiro dia do mês até hoje", THU10,
     (2026, 12, 1), (2026, 12, 11)),
])
def test_a_past_anchored_endpoint_steps_back_by_months(lang, text, anchor,
                                                      begin, end):
    span, rest = extract_timespan(text, lang, anchor)
    assert (span.start, span.end) == (AstroDate(*begin), AstroDate(*end))
    assert rest == ""
