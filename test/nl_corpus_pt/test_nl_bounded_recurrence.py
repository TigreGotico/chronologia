"""Bounded recurrence (pt): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT, occurrences at the rule frequency). UNTIL is resolved
against a fixed anchor so the RRULE is stable."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('toda sexta', 'FREQ=WEEKLY;BYDAY=FR', ''), ('toda segunda', 'FREQ=WEEKLY;BYDAY=MO', ''), ('diariamente', 'FREQ=DAILY', ''), ('semanalmente', 'FREQ=WEEKLY', ''), ('toda sexta até junho', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('diariamente durante duas semanas', 'FREQ=DAILY;COUNT=14', ''), ('diariamente durante uma semana', 'FREQ=DAILY;COUNT=7', ''), ('toda segunda durante 6 semanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('toda sexta durante três semanas', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "pt", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['sexta', '5 de junho'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "pt", anchor=ANCHOR) is None
