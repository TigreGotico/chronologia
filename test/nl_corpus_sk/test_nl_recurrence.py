# -*- coding: utf-8 -*-
"""Recurrence in sk: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "sk"

_CASES = [
    ('každý piatok', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('každý pondelok', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('denne', 'FREQ=DAILY', ''),
    ('týždenne', 'FREQ=WEEKLY', ''),
    ('mesačne', 'FREQ=MONTHLY', ''),
    ('ročne', 'FREQ=YEARLY', ''),
    ('každé 2 týždne', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('každé 3 dni', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['piatok', 'dnes'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
