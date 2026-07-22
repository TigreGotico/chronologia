# -*- coding: utf-8 -*-
"""Recurrence in sv: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "sv"

_CASES = [
    ('varje fredag', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('varje måndag', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('dagligen', 'FREQ=DAILY', ''),
    ('veckovis', 'FREQ=WEEKLY', ''),
    ('månatligen', 'FREQ=MONTHLY', ''),
    ('årligen', 'FREQ=YEARLY', ''),
    ('varje 2 veckor', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('varje 3 dagar', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['fredag', 'måndag'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
