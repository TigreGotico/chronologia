"""Bounded recurrence (id): base rules plus an until-date (-> UNTIL, via the
leading "sampai") or a for-duration (-> COUNT, via the leading "selama").
Resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

A = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ("setiap jumat", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("setiap senin", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("setiap minggu", "FREQ=WEEKLY", ""),
    ("setiap bulan", "FREQ=MONTHLY", ""),
    ("setiap jumat sampai juni", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("setiap senin sampai desember", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
    ("setiap senin selama 6 minggu", "FREQ=WEEKLY;COUNT=6;BYDAY=MO", ""),
    ("setiap hari selama 2 minggu", "FREQ=DAILY;COUNT=14", ""),
]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "id", anchor=A)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ["jumat", "5 juni"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "id", anchor=A) is None
