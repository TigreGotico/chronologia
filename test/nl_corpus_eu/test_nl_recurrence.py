# -*- coding: utf-8 -*-
"""Recurrence in eu: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "eu"

_CASES = [
    ('egunero', 'FREQ=DAILY', ''),
    ('astero', 'FREQ=WEEKLY', ''),
    ('hilero', 'FREQ=MONTHLY', ''),
    ('urtero', 'FREQ=YEARLY', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['ostirala', 'gaur'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
