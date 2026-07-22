# -*- coding: utf-8 -*-
"""Recurrence in id: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "id"

_CASES = [
    ('setiap jumat', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('setiap senin', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('harian', 'FREQ=DAILY', ''),
    ('mingguan', 'FREQ=WEEKLY', ''),
    ('bulanan', 'FREQ=MONTHLY', ''),
    ('tahunan', 'FREQ=YEARLY', ''),
    ('setiap 2 minggu', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('setiap 3 hari', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['jumat', 'hari ini'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
