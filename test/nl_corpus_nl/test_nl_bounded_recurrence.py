"""Bounded recurrence (nl): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('elke vrijdag', 'FREQ=WEEKLY;BYDAY=FR', ''), ('elke maandag', 'FREQ=WEEKLY;BYDAY=MO', ''), ('elke week', 'FREQ=WEEKLY', ''), ('elke vrijdag tot juni', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('elke maandag tot december', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('elke maandag gedurende 6 weken', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('elke week gedurende 4 weken', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "nl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['vrijdag', '5 juni'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "nl", anchor=ANCHOR) is None
