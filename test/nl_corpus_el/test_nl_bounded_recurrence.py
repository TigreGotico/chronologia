"""Bounded recurrence (el): base rules plus an until-date (-> UNTIL, via the
leading "μέχρι") or a for-duration (-> COUNT, via the leading "για")."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

A = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ("κάθε παρασκευή", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("κάθε δευτέρα", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("κάθε εβδομάδα", "FREQ=WEEKLY", ""),
    ("κάθε μήνα", "FREQ=MONTHLY", ""),
    ("κάθε παρασκευή μέχρι ιούνιο", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("κάθε δευτέρα μέχρι δεκέμβριο", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
    ("κάθε δευτέρα για 6 εβδομάδες", "FREQ=WEEKLY;COUNT=6;BYDAY=MO", ""),
    ("κάθε μέρα για 2 εβδομάδες", "FREQ=DAILY;COUNT=14", ""),
]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "el", anchor=A)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ["παρασκευή", "5 ιουνίου"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "el", anchor=A) is None
