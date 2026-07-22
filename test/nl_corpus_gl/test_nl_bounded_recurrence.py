"""Bounded recurrence (gl): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT). UNTIL resolved against a fixed anchor."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('cada venres', 'FREQ=WEEKLY;BYDAY=FR', ''), ('cada luns', 'FREQ=WEEKLY;BYDAY=MO', ''), ('cada semana', 'FREQ=WEEKLY', ''), ('cada mes', 'FREQ=MONTHLY', ''), ('cada venres ata xuño', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('cada luns ata decembro', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('cada luns durante 6 semanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('cada semana durante 4 semanas', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "gl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['venres', 'o 5 de xuño'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "gl", anchor=ANCHOR) is None
