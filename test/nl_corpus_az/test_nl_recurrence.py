# -*- coding: utf-8 -*-
"""Recurrence in az: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "az"

_CASES = [
    ('hər cümə', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('hər bazar ertəsi', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('gündəlik', 'FREQ=DAILY', ''),
    ('həftəlik', 'FREQ=WEEKLY', ''),
    ('aylıq', 'FREQ=MONTHLY', ''),
    ('illik', 'FREQ=YEARLY', ''),
    ('hər 2 həftə', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('hər 3 gün', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['cümə', 'bugün'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
