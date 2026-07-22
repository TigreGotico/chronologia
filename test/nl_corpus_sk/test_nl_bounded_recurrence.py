# -*- coding: utf-8 -*-
"""Bounded recurrence (sk): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The single-word for-marker resolves COUNT."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('každý piatok', 'FREQ=WEEKLY;BYDAY=FR'), ('každý pondelok', 'FREQ=WEEKLY;BYDAY=MO'), ('každý týždeň', 'FREQ=WEEKLY'), ('každý mesiac', 'FREQ=MONTHLY'), ('každý piatok do júna', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('každý pondelok do decembra', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "sk", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("každý pondelok počas 6 týždňov", "sk", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['piatok', '5. júna'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "sk", anchor=ANCHOR) is None
