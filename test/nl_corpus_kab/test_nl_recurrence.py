# -*- coding: utf-8 -*-
"""Recurrence in kab: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "kab"

_CASES = [
    ('yal lǧemɛa', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('yal letnayen', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('yal ass', 'FREQ=DAILY', ''),
    ('yal amalas', 'FREQ=WEEKLY', ''),
    ('yal 2 imalasen', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('yal 3 ussan', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['lǧemɛa', 'assa'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
