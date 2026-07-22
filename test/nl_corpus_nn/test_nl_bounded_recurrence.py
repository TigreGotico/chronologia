"""Bounded recurrence (nn): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('kvar fredag', 'FREQ=WEEKLY;BYDAY=FR', ''), ('kvar måndag', 'FREQ=WEEKLY;BYDAY=MO', ''), ('kvar veke', 'FREQ=WEEKLY', ''), ('kvar fredag til juni', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('kvar måndag til desember', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('kvar måndag i 6 veker', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('kvar veke i 4 veker', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "nn", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['fredag', '5. juni'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "nn", anchor=ANCHOR) is None
