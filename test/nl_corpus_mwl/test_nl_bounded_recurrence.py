# -*- coding: utf-8 -*-
"""Bounded recurrence (mwl): a base rule plus an until-date (``até`` -> UNTIL)
or a for-duration (``durante`` -> COUNT).  UNTIL resolved against a fixed
anchor (2017-06-27)."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ('cada sesta feira', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada sumana', 'FREQ=WEEKLY', ''),
    ('cada sesta feira até dezembre', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=FR', ''),
    ('cada segunda feira até setembre', 'FREQ=WEEKLY;UNTIL=20170901T000000;BYDAY=MO', ''),
    ('cada segunda feira durante 6 sumanas', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''),
    ('cada sesta feira durante 3 sumanas', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''),
    ('cada sumana durante 4 sumanas', 'FREQ=WEEKLY;COUNT=4', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "mwl", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['sesta feira', 'hoije'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "mwl", anchor=ANCHOR) is None
