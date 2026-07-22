"""Bounded recurrence (ms): base rules plus an until-date (-> UNTIL, via the
leading "sehingga") or a for-duration (-> COUNT, via the leading "selama")."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

A = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ("setiap jumaat", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("setiap isnin", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("setiap minggu", "FREQ=WEEKLY", ""),
    ("setiap bulan", "FREQ=MONTHLY", ""),
    ("setiap jumaat sehingga jun", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("setiap isnin sehingga disember", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
    ("setiap isnin selama 6 minggu", "FREQ=WEEKLY;COUNT=6;BYDAY=MO", ""),
    ("setiap hari selama 2 minggu", "FREQ=DAILY;COUNT=14", ""),
]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "ms", anchor=A)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ["jumaat", "5 jun"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "ms", anchor=A) is None
