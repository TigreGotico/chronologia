# -*- coding: utf-8 -*-
"""Recurrence in nb: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "nb"

_CASES = [
    ('hver fredag', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('hver mandag', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('daglig', 'FREQ=DAILY', ''),
    ('ukentlig', 'FREQ=WEEKLY', ''),
    ('månedlig', 'FREQ=MONTHLY', ''),
    ('årlig', 'FREQ=YEARLY', ''),
    ('hver 2 uker', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('hver 3 dager', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['fredag', 'mandag'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
