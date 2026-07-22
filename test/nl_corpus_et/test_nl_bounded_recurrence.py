"""Bounded recurrence (et): base rules plus an until-date (-> UNTIL) via the
leading "kuni", and a for-duration COUNT via the **postposed** "jooksul"
("<duration> jooksul" = for <duration>) -- the engine tries a leading marker
then a postposed one, so Estonian's trailing bound word resolves natively."""
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

def test_postposed_count_recurrence():
    got = extract_recurrence("iga esmaspäev 6 nädala jooksul", "et", anchor=A)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""


@pytest.mark.parametrize("text", ["reede", "5 juuni"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "et", anchor=A) is None
