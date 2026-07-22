# -*- coding: utf-8 -*-
"""Recurrence in el: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "el"

_CASES = [
    ('κάθε παρασκευή', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('κάθε δευτέρα', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('καθημερινά', 'FREQ=DAILY', ''),
    ('εβδομαδιαία', 'FREQ=WEEKLY', ''),
    ('μηνιαία', 'FREQ=MONTHLY', ''),
    ('ετήσια', 'FREQ=YEARLY', ''),
    ('κάθε 2 εβδομάδες', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('κάθε 3 μέρες', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['παρασκευή', 'σήμερα'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
