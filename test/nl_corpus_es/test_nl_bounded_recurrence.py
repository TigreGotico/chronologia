"""Bounded recurrence (es): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT, occurrences at the rule frequency). UNTIL is resolved
against a fixed anchor so the RRULE is stable."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('cada viernes', 'FREQ=WEEKLY;BYDAY=FR', ''), ('cada lunes', 'FREQ=WEEKLY;BYDAY=MO', ''), ('cada semana', 'FREQ=WEEKLY', ''), ('cada mes', 'FREQ=MONTHLY', ''), ('cada viernes hasta junio', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('cada lunes hasta diciembre', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''), ('cada lunes durante 6 semanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('cada viernes durante tres semanas', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''), ('cada semana durante 4 semanas', 'FREQ=WEEKLY;COUNT=4', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "es", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['viernes', 'el 5 de junio'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "es", anchor=ANCHOR) is None
