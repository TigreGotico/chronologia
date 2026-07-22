"""Bounded recurrence (fr): base rules plus an until-date (-> UNTIL) or a
for-duration (-> COUNT, occurrences at the rule frequency). UNTIL is resolved
against a fixed anchor so the RRULE is stable."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('chaque vendredi', 'FREQ=WEEKLY;BYDAY=FR', ''), ('chaque lundi', 'FREQ=WEEKLY;BYDAY=MO', ''), ('tous les jours pendant deux semaines', 'FREQ=DAILY;COUNT=14', ''), ('tous les jours pendant une semaine', 'FREQ=DAILY;COUNT=7', ''), ('chaque vendredi pendant trois semaines', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''), ('chaque lundi pendant 6 semaines', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''), ('chaque semaine pendant 4 semaines', 'FREQ=WEEKLY;COUNT=4', ''), ('chaque vendredi pendant deux semaines', 'FREQ=WEEKLY;COUNT=2;BYDAY=FR', ''), ('chaque mardi pendant 5 semaines', 'FREQ=WEEKLY;COUNT=5;BYDAY=TU', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "fr", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.parametrize("text", ['vendredi', '5 juin'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "fr", anchor=ANCHOR) is None
