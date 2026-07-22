# -*- coding: utf-8 -*-
"""Bounded recurrence (bg): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The for-marker 'в продължение на' is multiword, so COUNT is xfailed (ro precedent)."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('всеки петък', 'FREQ=WEEKLY;BYDAY=FR'), ('всеки понеделник', 'FREQ=WEEKLY;BYDAY=MO'), ('всяка седмица', 'FREQ=WEEKLY'), ('всеки месец', 'FREQ=MONTHLY'), ('всеки петък до юни', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('всеки понеделник до декември', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "bg", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


@pytest.mark.xfail(reason="multiword for-marker 'в продължение на' is not consumed as a "
                          "recurrence bound, so COUNT does not fire (bg)",
                   strict=True)
def test_count_recurrence():
    got = extract_recurrence("всеки понеделник в продължение на 6 седмици", "bg", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['петък', '5 юни'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "bg", anchor=ANCHOR) is None
