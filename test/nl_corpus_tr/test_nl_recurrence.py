# -*- coding: utf-8 -*-
"""Recurrence in tr: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "tr"

_CASES = [
    ('her cuma', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('her pazartesi', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('günlük', 'FREQ=DAILY', ''),
    ('haftalık', 'FREQ=WEEKLY', ''),
    ('aylık', 'FREQ=MONTHLY', ''),
    ('yıllık', 'FREQ=YEARLY', ''),
    ('her 2 hafta', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('her 3 gün', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['cuma', 'bugün'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
