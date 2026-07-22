# -*- coding: utf-8 -*-
"""Recurrence in pl: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pl"

_CASES = [
    ('każdy piątek', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('każdy poniedziałek', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('codziennie', 'FREQ=DAILY', ''),
    ('tygodniowo', 'FREQ=WEEKLY', ''),
    ('miesięcznie', 'FREQ=MONTHLY', ''),
    ('rocznie', 'FREQ=YEARLY', ''),
    ('co 2 tygodnie', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('co 3 dni', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['piątek', 'dziś'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
