"""Bounded recurrence (fy): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('elke freed', 'FREQ=WEEKLY;BYDAY=FR', ''), ('elke moandei', 'FREQ=WEEKLY;BYDAY=MO', ''), ('elke wike', 'FREQ=WEEKLY', ''), ('elke freed oant juny', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('elke moandei oant desimber', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "fy", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

def test_for_duration_count():
    got = extract_recurrence('elke freed foar 6 wiken', "fy", anchor=ANCHOR)
    assert got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=FR"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['freed', '5 juny'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "fy", anchor=ANCHOR) is None
