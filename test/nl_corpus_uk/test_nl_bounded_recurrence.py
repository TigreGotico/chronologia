# -*- coding: utf-8 -*-
"""Bounded recurrence (uk): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The single-word for-marker resolves COUNT."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [("кожної п'ятниці", 'FREQ=WEEKLY;BYDAY=FR'), ('кожного понеділка', 'FREQ=WEEKLY;BYDAY=MO'), ('кожного тижня', 'FREQ=WEEKLY'), ('кожного місяця', 'FREQ=MONTHLY'), ("кожної п'ятниці до червня", 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('кожного понеділка до грудня', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "uk", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("кожного понеділка протягом 6 тижнів", "uk", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ["п'ятницю", '5 червня'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "uk", anchor=ANCHOR) is None
