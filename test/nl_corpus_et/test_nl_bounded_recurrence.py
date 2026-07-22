"""Bounded recurrence (et): base rules plus an until-date (-> UNTIL) via the
leading "kuni". A for-duration COUNT bound would need a leading for-word;
Estonian marks it with the postposed "jooksul", which the engine's leading
scan does not reach, so COUNT is a documented limitation here."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

A = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ("iga reede", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("iga esmaspäev", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("iga nädal", "FREQ=WEEKLY", ""),
    ("iga kuu", "FREQ=MONTHLY", ""),
    ("iga reede kuni juuni", "FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR", ""),
    ("iga esmaspäev kuni detsember", "FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO", ""),
]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "et", anchor=A)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ["reede", "5 juuni"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "et", anchor=A) is None
