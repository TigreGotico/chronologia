"""Bounded recurrence (da): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('hver fredag', 'FREQ=WEEKLY;BYDAY=FR', ''), ('hver mandag', 'FREQ=WEEKLY;BYDAY=MO', ''), ('hver uge', 'FREQ=WEEKLY', ''), ('hver fredag indtil juni', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('hver mandag indtil december', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('hver mandag i 6 uger', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('hver uge i 4 uger', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "da", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['fredag', '5. juni'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "da", anchor=ANCHOR) is None
