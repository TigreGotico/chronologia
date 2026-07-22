# -*- coding: utf-8 -*-
"""Bounded recurrence (hr): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The single-word for-marker resolves COUNT."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('svaki petak', 'FREQ=WEEKLY;BYDAY=FR'), ('svaki ponedjeljak', 'FREQ=WEEKLY;BYDAY=MO'), ('svaki tjedan', 'FREQ=WEEKLY'), ('svaki mjesec', 'FREQ=MONTHLY'), ('svaki petak do lipnja', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('svaki ponedjeljak do prosinca', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "hr", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("svaki ponedjeljak tijekom 6 tjedana", "hr", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['petak', '5. lipnja'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "hr", anchor=ANCHOR) is None
