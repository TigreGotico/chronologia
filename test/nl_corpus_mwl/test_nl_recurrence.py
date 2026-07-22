# -*- coding: utf-8 -*-
"""Recurrence in mwl: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "mwl"

_CASES = [
    ('cada sesta feira', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada segunda feira', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('diariamente', 'FREQ=DAILY', ''),
    ('sumanalmente', 'FREQ=WEEKLY', ''),
    ('mensalmente', 'FREQ=MONTHLY', ''),
    ('anualmente', 'FREQ=YEARLY', ''),
    ('cada 2 sumanas', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('cada 3 dies', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['sesta feira', 'segunda feira'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
