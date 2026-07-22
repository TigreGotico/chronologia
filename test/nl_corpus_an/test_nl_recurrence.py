# -*- coding: utf-8 -*-
"""Recurrence in an: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "an"

_CASES = [
    ('cada viernes', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada luns', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('diariament', 'FREQ=DAILY', ''),
    ('semanalment', 'FREQ=WEEKLY', ''),
    ('mensualment', 'FREQ=MONTHLY', ''),
    ('anualment', 'FREQ=YEARLY', ''),
    ('cada 2 semanas', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('cada 3 diyas', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['viernes', 'luns'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
