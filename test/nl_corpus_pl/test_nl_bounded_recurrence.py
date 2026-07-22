# -*- coding: utf-8 -*-
"""Bounded recurrence (pl): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The single-word for-marker resolves COUNT."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('każdy piątek', 'FREQ=WEEKLY;BYDAY=FR'), ('każdy poniedziałek', 'FREQ=WEEKLY;BYDAY=MO'), ('każdy tydzień', 'FREQ=WEEKLY'), ('każdy miesiąc', 'FREQ=MONTHLY'), ('każdy piątek do czerwca', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('każdy poniedziałek do grudnia', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "pl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("każdy poniedziałek przez 6 tygodni", "pl", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['piątek', '5 czerwca'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "pl", anchor=ANCHOR) is None
