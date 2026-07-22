"""Bounded recurrence (ro): base rules plus an until-date (-> UNTIL).

Romanian's for-duration marker is the multiword "timp de" / "vreme de"; the
recurrence count-matcher only consumes single-token for-markers, so the COUNT
form is documented and xfail'd rather than forced into an unnatural single word.
"""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('fiecare vineri', 'FREQ=WEEKLY;BYDAY=FR', ''), ('fiecare luni', 'FREQ=WEEKLY;BYDAY=MO', ''), ('fiecare săptămână', 'FREQ=WEEKLY', ''), ('fiecare lună', 'FREQ=MONTHLY', ''), ('fiecare vineri până în iunie', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''), ('fiecare vineri până în decembrie', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=FR', '')]

@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "ro", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder

@pytest.mark.xfail(reason="Romanian for-duration marker 'timp de' is multiword; "
                          "recurrence COUNT matcher only consumes single-token markers",
                   strict=True)
def test_for_duration_count():
    got = extract_recurrence("fiecare vineri timp de 6 săptămâni", "ro", anchor=ANCHOR)
    assert got[0].to_string() == 'FREQ=WEEKLY;COUNT=6;BYDAY=FR'
    assert got[1] == ''

@pytest.mark.parametrize("text", ['vineri', '5 iunie'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "ro", anchor=ANCHOR) is None
