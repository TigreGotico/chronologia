# -*- coding: utf-8 -*-
"""Recurrence in ar: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ar"

_CASES = [
    ('كل جمعة', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('كل إثنين', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('يوميا', 'FREQ=DAILY', ''),
    ('أسبوعيا', 'FREQ=WEEKLY', ''),
    ('شهريا', 'FREQ=MONTHLY', ''),
    ('سنويا', 'FREQ=YEARLY', ''),
    ('كل 2 أسبوع', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('كل 3 يوم', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['جمعة', 'اليوم'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
