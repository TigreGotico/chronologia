"""Bounded recurrence (oc): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('cada divendres', 'FREQ=WEEKLY;BYDAY=FR', ''), ('cada diluns', 'FREQ=WEEKLY;BYDAY=MO', ''), ('cada setmana', 'FREQ=WEEKLY', ''), ('cada mes', 'FREQ=MONTHLY', ''), ('cada divendres fins a junh', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('cada diluns fins a decembre', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('cada diluns pendent 6 setmanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('cada setmana pendent 4 setmanas', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "oc", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['divendres', 'lo 5 de junh'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "oc", anchor=ANCHOR) is None
