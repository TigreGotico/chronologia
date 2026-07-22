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
    ("first monday of every month", "FREQ=MONTHLY;BYDAY=1MO", ""),
    ("last friday of every month", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("the third thursday of november", "FREQ=YEARLY;BYMONTH=11;BYDAY=3TH", ""),
    # date-anchored recurrence: the single-span engine reads the date part.
    ("every 10th of may", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every may 10", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every year on may 10", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("the 10th of every month", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("every month on the 10th", "FREQ=MONTHLY;BYMONTHDAY=10", ""),
    ("the 1st of every month", "FREQ=MONTHLY;BYMONTHDAY=1", ""),
    ("every christmas", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25", ""),
    ("every halloween", "FREQ=YEARLY;BYMONTH=10;BYMONTHDAY=31", ""),
    ("every valentines day", "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=14", ""),
    ("every thanksgiving", "FREQ=YEARLY;BYMONTH=11;BYDAY=4TH", ""),
    # clock pin: BYHOUR / BYMINUTE fold onto the rule.
    ("daily at 9", "FREQ=DAILY;BYHOUR=9", ""),
    ("every day at 9am", "FREQ=DAILY;BYHOUR=9", ""),
    ("daily at noon", "FREQ=DAILY;BYHOUR=12", ""),
    ("every day at midnight", "FREQ=DAILY;BYHOUR=0", ""),
    ("every wednesday at 9", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9", ""),
    ("every wednesday at 9:30", "FREQ=WEEKLY;BYDAY=WE;BYHOUR=9;BYMINUTE=30", ""),
    ("every 10th of may at 9am", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10;BYHOUR=9", ""),
]


# Movable-feast recurrence: a real object whose occurrences() works but whose
# to_string() refuses to lie (no RFC 5545 rule expresses a computus/lunar feast).
from chronologia.recurrence import HolidayRecurrence   # noqa: E402


@pytest.mark.parametrize("text,key", [
    ("every easter", "easter"),
    ("every good friday", "good_friday"),
])
def test_movable_holiday_recurrence(text, key):
    got = extract_recurrence(text, LANG)
    assert got is not None
    assert got[0] == HolidayRecurrence(key)
    assert got[1] == ""
    with pytest.raises(ValueError):
        got[0].to_string()


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
