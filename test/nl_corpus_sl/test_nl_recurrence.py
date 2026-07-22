# -*- coding: utf-8 -*-
"""Recurrence in sl: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "sl"

_CASES = [
    ('vsak petek', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('vsak ponedeljek', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('dnevno', 'FREQ=DAILY', ''),
    ('tedensko', 'FREQ=WEEKLY', ''),
    ('mesečno', 'FREQ=MONTHLY', ''),
    ('letno', 'FREQ=YEARLY', ''),
    ('vsak 2 tedna', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('vsak 3 dni', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['petek', 'danes'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
