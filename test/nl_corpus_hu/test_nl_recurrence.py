# -*- coding: utf-8 -*-
"""Recurrence in hu: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "hu"

_CASES = [
    ('minden péntek', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('minden hétfő', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('naponta', 'FREQ=DAILY', ''),
    ('hetente', 'FREQ=WEEKLY', ''),
    ('havonta', 'FREQ=MONTHLY', ''),
    ('évente', 'FREQ=YEARLY', ''),
    ('minden 2 hét', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('minden 3 nap', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['péntek', 'ma'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
