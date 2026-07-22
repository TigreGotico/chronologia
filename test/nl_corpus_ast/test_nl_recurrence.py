# -*- coding: utf-8 -*-
"""Recurrence in ast: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ast"

_CASES = [
    ('cada vienres', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada llunes', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('diariamente', 'FREQ=DAILY', ''),
    ('selmanalmente', 'FREQ=WEEKLY', ''),
    ('mensualmente', 'FREQ=MONTHLY', ''),
    ('añalmente', 'FREQ=YEARLY', ''),
    ('cada 2 selmanes', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('cada 3 díes', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['vienres', 'llunes'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
