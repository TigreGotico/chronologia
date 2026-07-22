# -*- coding: utf-8 -*-
"""Bounded recurrence (he): a base rule plus an until-date (``עד`` -> UNTIL)
or a for-duration (``למשך`` -> COUNT).  UNTIL resolved against a fixed anchor.

Hebrew bare weekday names that also read as ordinals (שני "Monday"/"second")
do not resolve as a bare weekday in the recurrence grammar; Friday (שישי) and
the plain week rule are used here."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ('כל שישי', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('כל שבוע', 'FREQ=WEEKLY', ''),
    ('כל שישי עד יוני', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''),
    ('כל שישי עד דצמבר', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=FR', ''),
    ('כל שישי למשך 3 שבועות', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''),
    ('כל שבוע למשך 4 שבועות', 'FREQ=WEEKLY;COUNT=4', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "he", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['שישי', 'היום'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "he", anchor=ANCHOR) is None
