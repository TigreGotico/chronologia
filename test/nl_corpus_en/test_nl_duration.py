"""Durations: a *length* of time (not a point on the calendar).

The contract is the public ``extract_duration(text, "en")`` edge, returning a
:class:`datetime.timedelta` plus the leftover text.  Every expected value is
hand-derived seconds arithmetic that never touches the parser.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "en"

# (text, expected timedelta) -- fixed-width units only.
_CASES = [
    ("5 minutes", timedelta(minutes=5)),
    ("1 minute", timedelta(minutes=1)),
    ("45 minutes", timedelta(minutes=45)),
    ("90 minutes", timedelta(minutes=90)),
    ("ninety minutes", timedelta(minutes=90)),
    ("2 hours", timedelta(hours=2)),
    ("an hour", timedelta(hours=1)),
    ("4 hours", timedelta(hours=4)),
    ("a day", timedelta(days=1)),
    ("2 days", timedelta(days=2)),
    ("3 weeks", timedelta(weeks=3)),
    ("a fortnight", timedelta(weeks=2)),
    # fractional
    ("half an hour", timedelta(minutes=30)),
    ("quarter of an hour", timedelta(minutes=15)),
    ("a quarter of an hour", timedelta(minutes=15)),
    ("three quarters of an hour", timedelta(minutes=45)),
    ("an hour and a half", timedelta(hours=1, minutes=30)),
    ("one and a half hours", timedelta(hours=1, minutes=30)),
    ("two and a half hours", timedelta(hours=2, minutes=30)),
    # seconds (fixed-width, second-precise)
    ("30 seconds", timedelta(seconds=30)),
    ("5 sec", timedelta(seconds=5)),
    ("45 secs", timedelta(seconds=45)),
    # compound
    ("2 days 4 hours", timedelta(days=2, hours=4)),
    ("1 hour 30 minutes", timedelta(hours=1, minutes=30)),
    ("5 days 6 hours 30 minutes", timedelta(days=5, hours=6, minutes=30)),
    # compound: every component sums -- trailing parts must not be dropped.
    ("a minute and thirty seconds", timedelta(minutes=1, seconds=30)),
    ("two hours and fifteen minutes", timedelta(hours=2, minutes=15)),
    ("one hour thirty minutes", timedelta(hours=1, minutes=30)),
    ("three days and twelve hours", timedelta(days=3, hours=12)),
    ("1 hour 2 minutes 3 seconds", timedelta(hours=1, minutes=2, seconds=3)),
    # the "and a half" idiom is HALF OF THE PRECEDING UNIT, distinct from
    # "and <n> <smaller-unit>": both must land on 90s / 5400s respectively.
    ("a minute and a half", timedelta(minutes=1, seconds=30)),
    ("an hour and a half", timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


# remainder: the non-duration words come back untouched.
@pytest.mark.parametrize("text,expected,remainder", [
    ("5 minutes please", timedelta(minutes=5), "please"),
    ("wait 10 minutes", timedelta(minutes=10), "wait"),
    ("in a fortnight from now", timedelta(weeks=2), "in from now"),
])
def test_duration_remainder(text, expected, remainder):
    got = extract_duration(text, LANG)
    assert got == (expected, remainder)


# adversarial: not a fixed-width duration -> None (never a spurious span).
@pytest.mark.parametrize("text", [
    "a second chance",   # ordinal "second"/idiom, not 1 second
    "2 months",          # calendar-ambiguous unit, out of scope
    "next year",         # a reference, not a length
    "hello world",       # nothing temporal
])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
