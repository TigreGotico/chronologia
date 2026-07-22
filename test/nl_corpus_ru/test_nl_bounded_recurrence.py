# -*- coding: utf-8 -*-
"""Bounded recurrence (ru): base rules plus an until-date (-> UNTIL) via the
open-range marker or a for-duration (-> COUNT). UNTIL resolved against a fixed
anchor. The for-marker 'в течение' is multiword, so COUNT is xfailed (ro precedent)."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [('каждую пятницу', 'FREQ=WEEKLY;BYDAY=FR'), ('каждый понедельник', 'FREQ=WEEKLY;BYDAY=MO'), ('каждую неделю', 'FREQ=WEEKLY'), ('каждый месяц', 'FREQ=MONTHLY'), ('каждую пятницу до июня', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR'), ('каждый понедельник до декабря', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO')]


@pytest.mark.parametrize("text,rrule", _CASES)
def test_bounded_recurrence(text, rrule):
    got = extract_recurrence(text, "ru", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == ""


def test_count_recurrence():
    got = extract_recurrence("каждый понедельник в течение 6 недель", "ru", anchor=ANCHOR)
    assert got is not None and got[0].to_string() == "FREQ=WEEKLY;COUNT=6;BYDAY=MO"
    assert got[1] == ""

@pytest.mark.parametrize("text", ['пятницу', '5 июня'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "ru", anchor=ANCHOR) is None
