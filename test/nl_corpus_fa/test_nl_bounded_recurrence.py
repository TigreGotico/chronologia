# -*- coding: utf-8 -*-
"""Bounded recurrence (fa): a base rule plus an until-date (``تا`` -> UNTIL)
or a for-duration (``برای`` -> COUNT).  UNTIL resolved against a fixed anchor.

Note: the two-word ``به مدت`` also means "for the duration of" but the
recurrence grammar binds only single-token for-markers, so ``برای`` is used
for the COUNT cases."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ('هر جمعه', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('هر هفته', 'FREQ=WEEKLY', ''),
    ('هر جمعه تا ژوئن', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''),
    ('هر جمعه تا دسامبر', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=FR', ''),
    ('هر جمعه برای 3 هفته', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''),
    ('هر هفته برای 4 هفته', 'FREQ=WEEKLY;COUNT=4', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "fa", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['جمعه', 'امروز'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "fa", anchor=ANCHOR) is None
