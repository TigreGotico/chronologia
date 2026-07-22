# -*- coding: utf-8 -*-
"""Recurrence in oc: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "oc"

_CASES = [
    ('cada divendres', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('cada diluns', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('jornalièrament', 'FREQ=DAILY', ''),
    ('setmanalament', 'FREQ=WEEKLY', ''),
    ('mensualament', 'FREQ=MONTHLY', ''),
    ('annadièirament', 'FREQ=YEARLY', ''),
    ('cada 2 setmanas', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('cada 3 jorns', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['divendres', 'diluns'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
