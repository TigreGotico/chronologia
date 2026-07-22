"""Recurrence: a recurring phrase -> an RFC 5545 ``RRULE``.

The contract is ``extract_recurrence(text, "en")`` -> the repo's
:class:`~chronologia.recurrence.Recurrence` plus the leftover text.  Expected
values are the hand-written canonical RRULE strings.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

# (text, expected RRULE string, expected remainder)
_CASES = [
    ("every friday", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("every monday", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("every day", "FREQ=DAILY", ""),
    ("every week", "FREQ=WEEKLY", ""),
    ("every month", "FREQ=MONTHLY", ""),
    ("every year", "FREQ=YEARLY", ""),
    ("every other week", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("every 2 weeks", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("every other tuesday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU", ""),
    ("every weekday", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
    ("daily", "FREQ=DAILY", ""),
    ("weekly", "FREQ=WEEKLY", ""),
    ("monthly", "FREQ=MONTHLY", ""),
    ("annually", "FREQ=YEARLY", ""),
    ("daily at 9", "FREQ=DAILY", "at 9"),
    ("first monday of every month", "FREQ=MONTHLY;BYDAY=1MO", ""),
    ("last friday of every month", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("the third thursday of november", "FREQ=YEARLY;BYMONTH=11;BYDAY=3TH", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# Bounded recurrence: an "until <date>" folds to UNTIL; a "for <duration>"
# folds to COUNT -- the number of occurrences the fixed-width duration spans at
# the rule's frequency (14 days -> 14 daily hits; 6 weeks -> 6 weekly hits).
# The UNTIL date is resolved against a fixed anchor so the RRULE is stable.
from datetime import datetime               # noqa: E402

_BOUND_ANCHOR = datetime(2017, 6, 27, 13, 4)
_BOUND_CASES = [
    ("every friday until june", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("every monday until december", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
    ("daily until 2020", "FREQ=DAILY;UNTIL=20200101T000000", ""),
    ("every week till march", "FREQ=WEEKLY;UNTIL=20170301T000000", ""),
    ("daily for two weeks", "FREQ=DAILY;COUNT=14", ""),
    ("daily for a week", "FREQ=DAILY;COUNT=7", ""),
    ("every day for 3 days", "FREQ=DAILY;COUNT=3", ""),
    ("every monday for 6 weeks", "FREQ=WEEKLY;COUNT=6;BYDAY=MO", ""),
    ("every friday for three weeks", "FREQ=WEEKLY;COUNT=3;BYDAY=FR", ""),
    ("weekly for 4 weeks", "FREQ=WEEKLY;COUNT=4", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _BOUND_CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_BOUND_ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


# adversarial: a one-off reference is not a recurrence.
@pytest.mark.parametrize("text", [
    "friday", "next friday", "in 3 days", "june 5th",
])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
