"""Bounded recurrence (de): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT, occurrences at the rule frequency). UNTIL is resolved
against a fixed anchor so the RRULE is stable."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('jeden freitag', 'FREQ=WEEKLY;BYDAY=FR', ''), ('jeden montag', 'FREQ=WEEKLY;BYDAY=MO', ''), ('täglich für zwei wochen', 'FREQ=DAILY;COUNT=14', ''), ('täglich für eine woche', 'FREQ=DAILY;COUNT=7', ''), ('jeden freitag bis juni', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('jeden montag bis dezember', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('jeden montag für 6 wochen', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('jeden freitag für drei wochen', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''), ('jede woche', 'FREQ=WEEKLY', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "de", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['freitag', '5. juni'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "de", anchor=ANCHOR) is None
