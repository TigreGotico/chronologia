"""A weekday beside a day word names the same day, or no day, en.

In "tomorrow, sunday" the weekday is an apposition to "tomorrow": it names
the same day, so it does not stay in the remainder.  "tomorrow monday" said
on a Saturday names no single day, and the reading is refused.

Anchor Saturday 2026-10-17 12:00; gold from datetime arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_candidates, extract_timespan
from chronologia.astrodate import AstroDate

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,offset", [
    ("tomorrow sunday", 1),
    ("tomorrow, sunday", 1),
    ("yesterday friday", -1),
    ("today saturday", 0),
])
def test_day_word_with_its_own_weekday(text, offset):
    day = SATURDAY.replace(hour=0) + timedelta(days=offset)
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert span.start == AstroDate(day.year, day.month, day.day)
    assert rest == ""


@pytest.mark.parametrize("text", ["tomorrow monday", "yesterday sunday"])
def test_day_word_with_another_weekday_is_refused(text):
    assert extract_timespan(text, "en", SATURDAY) is None


def test_a_sentence_end_stops_the_apposition():
    r = extract_timespan("see you tomorrow. monday is busy", "en", SATURDAY)
    assert r is not None, "the sentence with tomorrow did not parse"
    day = SATURDAY.replace(hour=0) + timedelta(days=1)
    assert r[0].start == AstroDate(day.year, day.month, day.day)
    assert r[1] == "see you monday is busy"


def test_candidates_agree_across_a_sentence_end():
    text = "see you tomorrow. monday is busy"
    top = extract_candidates(text, "en", SATURDAY)[0]
    span, rest = extract_timespan(text, "en", SATURDAY)
    assert (top.span.start, top.remainder) == (span.start, rest)


def test_a_marked_weekday_is_not_an_apposition():
    # "next monday" is its own date, not a label on "tomorrow": the phrase
    # is not refused, and the marked weekday is not folded away.
    r = extract_timespan("tomorrow next monday", "en", SATURDAY)
    assert r is not None, "'tomorrow next monday' was refused"
    day = SATURDAY.replace(hour=0) + timedelta(days=1)
    assert r[0].start == AstroDate(day.year, day.month, day.day)
    assert r[1] == "next monday"


@pytest.mark.parametrize("text,start,end,rest", [
    ("from today until tomorrow. monday is busy",
     datetime(2026, 10, 17), datetime(2026, 10, 19), "monday is busy"),
    ("from today to tomorrow; monday off",
     datetime(2026, 10, 17), datetime(2026, 10, 19), "monday off"),
    ("until tomorrow. monday is busy",
     SATURDAY, datetime(2026, 10, 19), "monday is busy"),
])
def test_a_range_endpoint_does_not_fold_across_a_sentence_end(
        text, start, end, rest):
    # Today is Saturday 17; the range runs through Sunday 18, so its end is
    # the start of Monday 19.  "until" opens the range at the anchor.
    span, remainder = extract_timespan(text, "en", SATURDAY)
    assert (span.start, span.end) == (
        AstroDate(start.year, start.month, start.day, start.hour),
        AstroDate(end.year, end.month, end.day))
    assert remainder == rest
