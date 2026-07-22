# -*- coding: utf-8 -*-
"""Recurrence in fy: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fy"

_CASES = [
    ('elke freed', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('elke moandei', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('deistich', 'FREQ=DAILY', ''),
    ('wykliks', 'FREQ=WEEKLY', ''),
    ('moanliks', 'FREQ=MONTHLY', ''),
    ('jierliks', 'FREQ=YEARLY', ''),
    ('elke 2 wiken', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('elke 3 dagen', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['freed', 'moandei'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
