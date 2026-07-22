# -*- coding: utf-8 -*-
"""Recurrence in ro: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ro"

_CASES = [
    ('fiecare vineri', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('fiecare luni', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('zilnic', 'FREQ=DAILY', ''),
    ('săptămânal', 'FREQ=WEEKLY', ''),
    ('lunar', 'FREQ=MONTHLY', ''),
    ('anual', 'FREQ=YEARLY', ''),
    ('fiecare 2 săptămâni', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('fiecare 3 zile', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['vineri', 'luni'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
