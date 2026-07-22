"""Bounded recurrence (ast): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('cada vienres', 'FREQ=WEEKLY;BYDAY=FR', ''), ('cada llunes', 'FREQ=WEEKLY;BYDAY=MO', ''), ('cada selmana', 'FREQ=WEEKLY', ''), ('cada mes', 'FREQ=MONTHLY', ''), ('cada vienres hasta xunu', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('cada llunes hasta avientu', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('cada llunes durante 6 selmanes', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('cada selmana durante 4 selmanes', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "ast", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['vienres', 'el 5 de xunu'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "ast", anchor=ANCHOR) is None
