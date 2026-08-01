# -*- coding: utf-8 -*-
"""R20: multi-ordinal BYDAY lists and last-weekday BYSETPOS in recurrences.

The recurrence finders read the spelled-number FOLDED stream, which merges a
number-word run across "and" ("first and third" -> "3"), silently dropping
entries from an ordinal-weekday list.  These lock the pre-fold recovery and the
business-day BYSETPOS idiom.
"""
from datetime import datetime

from chronologia import extract_recurrence

_A = datetime(2017, 6, 27, 13, 4)


def _rrule(text, lang="en"):
    r = extract_recurrence(text, lang, _A)
    return (r[0].to_string(), r.remainder) if r else (None, None)


def test_multi_ordinal_byday_list_not_collapsed():
    # "first and third" must not fold to a single "3"
    assert _rrule("the first and third monday of every month") == (
        "FREQ=MONTHLY;BYDAY=1MO,3MO", "")
    assert _rrule("every second and fourth tuesday") == (
        "FREQ=MONTHLY;BYDAY=2TU,4TU", "")


def test_last_and_first_weekday_of_month_bysetpos():
    assert _rrule("the last weekday of every month") == (
        "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1", "")
    assert _rrule("the first weekday of every month") == (
        "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1", "")


def test_recurrence_no_regressions():
    # single-ordinal named weekday, both readings, unchanged
    assert _rrule("the last friday of every month") == (
        "FREQ=MONTHLY;BYDAY=-1FR", "")
    assert _rrule("the third tuesday of the month") == (
        "FREQ=MONTHLY;BYDAY=3TU", "")
    assert _rrule("every third tuesday") == ("FREQ=WEEKLY;INTERVAL=3;BYDAY=TU", "")
    assert _rrule("the last monday of november") == (
        "FREQ=YEARLY;BYMONTH=11;BYDAY=-1MO", "")
    # plain weekday list still needs the determiner
    assert extract_recurrence("monday wednesday and friday", "en", _A) is None
    assert _rrule("every monday and friday") == ("FREQ=WEEKLY;BYDAY=MO,FR", "")
    # interval / count / until forms unaffected
    assert _rrule("every other week") == ("FREQ=WEEKLY;INTERVAL=2", "")
    assert _rrule("every day for 10 days") == ("FREQ=DAILY;COUNT=10", "")
    assert _rrule("every friday until september") == (
        "FREQ=WEEKLY;UNTIL=20170901T000000;BYDAY=FR", "")
