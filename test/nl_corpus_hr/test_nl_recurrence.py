# -*- coding: utf-8 -*-
"""Recurrence in hr: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "hr"

_CASES = [
    ('svaki petak', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('svaki ponedjeljak', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('dnevno', 'FREQ=DAILY', ''),
    ('tjedno', 'FREQ=WEEKLY', ''),
    ('mjesečno', 'FREQ=MONTHLY', ''),
    ('godišnje', 'FREQ=YEARLY', ''),
    ('svaki 2 tjedna', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('svaki 3 dana', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['petak', 'danas'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
