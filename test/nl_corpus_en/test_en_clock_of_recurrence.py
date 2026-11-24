# -*- coding: utf-8 -*-
"""The "of" before a recurrence that modifies a noun stays with the words before the clock, en."""
import pytest

from chronologia.extract import extract_recurrence

from ._corpus import ANCHOR


@pytest.mark.parametrize("text,rule,remainder", [
    ("remind me at 9 of every monday meeting", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", "remind me of meeting"),
    ("remind me at 5 of each friday deadline", "FREQ=WEEKLY;BYDAY=FR;BYHOUR=5", "remind me of deadline"),
    ("remind me at 8 of daily medication", "FREQ=DAILY;BYHOUR=8", "remind me of medication"),
    ("remind me at 7 of monthly bills", "FREQ=MONTHLY;BYHOUR=7", "remind me of bills"),
])
def test_of_stays_before_the_clock(text, rule, remainder):
    r = extract_recurrence(text, "en", ANCHOR)
    assert (r.recurrence.to_string(), r.remainder) == (rule, remainder)
