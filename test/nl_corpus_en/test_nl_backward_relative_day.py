"""Backward relative-day idioms -- the "before last" / "after next"
superlative-relative forms and the "<weekday> ago" / "<N-unit> ago
<weekday>" family, hand-derived against the Tuesday 2017-06-27 13:04 anchor.

Each of these formerly resolved FORWARD or dropped its qualifier:
"the Tuesday before last" pointed at a *future* Tuesday and stranded
"the before last"; "a Monday ago" gave *next* Monday; "a week ago
Tuesday" stranded the weekday; "the morning after next" gave today's
(already-elapsed) morning.  They now point backward / skip-ahead
correctly, consuming the whole phrase.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, span, start, start_end, nomatch

_MID = ANCHOR.replace(hour=0, minute=0)


def _rem(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


# -- "the <weekday> before last": two occurrences back --------------------

@pytest.mark.parametrize("text,expected", [
    # last Tuesday is 06-20; the one before that is 06-13
    ("the Tuesday before last", _MID - timedelta(days=14)),   # 2017-06-13
    ("Tuesday before last", _MID - timedelta(days=14)),
    # last Friday is 06-23; before last is 06-16
    ("the Friday before last", _MID - timedelta(days=11)),    # 2017-06-16
    # last Monday is 06-26; before last is 06-19
    ("the Monday before last", _MID - timedelta(days=8)),     # 2017-06-19
    # last Sunday is 06-25; before last is 06-18
    ("the Sunday before last", _MID - timedelta(days=9)),     # 2017-06-18
])
def test_weekday_before_last(text, expected):
    assert start(text) == ad(expected)
    assert _rem(text) == ""


def test_weekday_before_last_is_day_wide():
    assert span("the Tuesday before last").width == timedelta(days=1)


# -- "the week / month before last": whole calendar period two back -------

def test_week_before_last():
    s, e = start_end("the week before last")
    # last week is [06-19, 06-26); the week before that is [06-12, 06-19)
    assert s == ad(_MID - timedelta(days=15))                 # 2017-06-12
    assert e == ad(_MID - timedelta(days=8))                  # 2017-06-19
    assert _rem("the week before last") == ""


def test_month_before_last():
    s, e = start_end("the month before last")
    # anchor June; last month May; before last April
    assert (s.year, s.month, s.day) == (2017, 4, 1)
    assert (e.year, e.month, e.day) == (2017, 5, 1)


# -- "the night before last": daypart band two nights ago -----------------

def test_night_before_last():
    s, e = start_end("the night before last")
    # night band anchored to 06-25: [06-25 21:00, 06-26 06:00)
    assert (s.year, s.month, s.day, s.hour) == (2017, 6, 25, 21)
    assert (e.year, e.month, e.day, e.hour) == (2017, 6, 26, 6)
    assert _rem("the night before last") == ""


# -- "a <weekday> ago": the most recent past occurrence -------------------

@pytest.mark.parametrize("text,expected", [
    ("a Monday ago", _MID - timedelta(days=1)),      # last Monday 06-26
    ("a Tuesday ago", _MID - timedelta(days=7)),     # last Tuesday 06-20
    ("a Friday ago", _MID - timedelta(days=4)),      # last Friday 06-23
    ("a Sunday ago", _MID - timedelta(days=2)),      # last Sunday 06-25
])
def test_weekday_ago(text, expected):
    assert start(text) == ad(expected)
    assert _rem(text) == ""


# -- "<N-unit> ago <weekday>": weekday within the week N units back --------

def test_a_week_ago_weekday():
    # a week ago lands on Tue 06-20; the Tuesday of that week is 06-20
    assert start("a week ago Tuesday") == ad(_MID - timedelta(days=7))
    assert span("a week ago Tuesday").width == timedelta(days=1)   # whole day
    assert _rem("a week ago Tuesday") == ""


def test_a_week_ago_weekday_other_day():
    # the Monday of the week that was a week ago (Mon 06-19)
    assert start("a week ago Monday") == ad(_MID - timedelta(days=8))


def test_a_fortnight_ago_weekday():
    # a fortnight ago lands on Tue 06-13; the Monday of that week is 06-12
    assert start("a fortnight ago Monday") == ad(_MID - timedelta(days=15))
    # the returned day must actually be a Monday, not the fortnight's Tuesday
    assert start("a fortnight ago Monday").day == 12
    assert _rem("a fortnight ago Monday") == ""


# -- "the <X> after next": skip one (next-next) ---------------------------

def test_day_after_next():
    assert start("the day after next") == ad(_MID + timedelta(days=2))  # 06-29
    assert span("the day after next").width == timedelta(days=1)
    assert _rem("the day after next") == ""


def test_morning_after_next():
    s, e = start_end("the morning after next")
    # morning band on 06-29: [06-29 06:00, 06-29 12:00)
    assert (s.year, s.month, s.day, s.hour) == (2017, 6, 29, 6)
    assert (e.year, e.month, e.day, e.hour) == (2017, 6, 29, 12)
    assert _rem("the morning after next") == ""


def test_week_after_next_is_a_deferred_gap():
    # "the week after next" is a DEFERRED coarser-offset gap the repo
    # deliberately leaves unresolved (test_nl_gap_residue): no fabricated span.
    nomatch("the week after next")


# -- regression pins: the plain last/next/ago/before forms are unchanged ---

@pytest.mark.parametrize("text,expected", [
    ("last tuesday", _MID - timedelta(days=7)),
    ("next tuesday", _MID + timedelta(days=7)),
    ("last monday", _MID - timedelta(days=1)),
    ("yesterday", _MID - timedelta(days=1)),
])
def test_plain_forms_unchanged(text, expected):
    assert start(text) == ad(expected)


def test_a_week_ago_unchanged():
    # bare "a week ago" keeps the anchor time-of-day (offset family)
    assert start("a week ago") == ad(ANCHOR - timedelta(weeks=1))


def test_last_week_unchanged():
    s, e = start_end("last week")
    assert s == ad(_MID - timedelta(days=8))                  # 2017-06-19
    assert e == ad(_MID - timedelta(days=1))                  # 2017-06-26


def test_tomorrow_morning_unchanged():
    s, e = start_end("tomorrow morning")
    assert (s.year, s.month, s.day, s.hour) == (2017, 6, 28, 6)
    assert (e.year, e.month, e.day, e.hour) == (2017, 6, 28, 12)


def test_the_week_before_still_incomplete():
    # "the week before" (no "last") is not a complete reference on its own
    nomatch("the week before")
