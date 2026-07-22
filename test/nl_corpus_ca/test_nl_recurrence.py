# -*- coding: utf-8 -*-
"""Recurrence in ca: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ca"

_CASES = [
    ('cada divendres', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada dilluns', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('diàriament', 'FREQ=DAILY', ''),
    ('setmanalment', 'FREQ=WEEKLY', ''),
    ('mensualment', 'FREQ=MONTHLY', ''),
    ('anualment', 'FREQ=YEARLY', ''),
    ('cada 2 setmanes', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('cada 3 dies', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['divendres', 'dilluns'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
