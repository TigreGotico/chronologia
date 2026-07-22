# -*- coding: utf-8 -*-
"""Recurrence in nn: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "nn"

_CASES = [
    ('kvar fredag', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('kvar måndag', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('dagleg', 'FREQ=DAILY', ''),
    ('vekeleg', 'FREQ=WEEKLY', ''),
    ('månadleg', 'FREQ=MONTHLY', ''),
    ('årleg', 'FREQ=YEARLY', ''),
    ('kvar 2 veker', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('kvar 3 dagar', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['fredag', 'måndag'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
