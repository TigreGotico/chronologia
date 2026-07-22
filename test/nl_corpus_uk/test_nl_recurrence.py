# -*- coding: utf-8 -*-
"""Recurrence in uk: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "uk"

_CASES = [
    ("кожна п'ятниця", 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('кожен понеділок', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('щодня', 'FREQ=DAILY', ''),
    ('щотижня', 'FREQ=WEEKLY', ''),
    ('щомісяця', 'FREQ=MONTHLY', ''),
    ('щороку', 'FREQ=YEARLY', ''),
    ('кожні 2 тижні', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('кожні 3 дні', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["п'ятниця", 'сьогодні'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
