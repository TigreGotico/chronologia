# -*- coding: utf-8 -*-
"""Recurrence in he: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "he"

_CASES = [
    ('כל שישי', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('כל יום ראשון', 'FREQ=WEEKLY;BYDAY=SU', ''),
    ('יומי', 'FREQ=DAILY', ''),
    ('שבועי', 'FREQ=WEEKLY', ''),
    ('חודשי', 'FREQ=MONTHLY', ''),
    ('שנתי', 'FREQ=YEARLY', ''),
    ('כל 2 שבועות', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('כל 3 ימים', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['שישי', 'היום'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
