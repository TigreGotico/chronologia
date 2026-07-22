# -*- coding: utf-8 -*-
"""Bounded recurrence (ar): a base rule plus an until-date (``حتى`` -> UNTIL)
or a for-duration (``لمدة`` -> COUNT, occurrences at the rule frequency).
UNTIL is resolved against a fixed anchor so the RRULE is stable."""
from datetime import datetime
import pytest
from chronologia.extract import extract_recurrence

ANCHOR = datetime(2017, 6, 27, 13, 4)
_CASES = [
    ('كل جمعة', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('كل إثنين', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('كل جمعة حتى يونيو', 'FREQ=WEEKLY;UNTIL=20170601T000000;BYDAY=FR', ''),
    ('كل إثنين حتى ديسمبر', 'FREQ=WEEKLY;UNTIL=20171201T000000;BYDAY=MO', ''),
    ('كل إثنين لمدة 6 أسابيع', 'FREQ=WEEKLY;COUNT=6;BYDAY=MO', ''),
    ('كل جمعة لمدة 3 أسابيع', 'FREQ=WEEKLY;COUNT=3;BYDAY=FR', ''),
    ('كل أسبوع لمدة 4 أسابيع', 'FREQ=WEEKLY;COUNT=4', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_bounded_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, "ar", anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['جمعة', 'اليوم'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, "ar", anchor=ANCHOR) is None
