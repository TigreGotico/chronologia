# -*- coding: utf-8 -*-
"""Recurrence in bg: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "bg"

_CASES = [
    ('всеки петък', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('всеки понеделник', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('ежедневно', 'FREQ=DAILY', ''),
    ('седмично', 'FREQ=WEEKLY', ''),
    ('месечно', 'FREQ=MONTHLY', ''),
    ('годишно', 'FREQ=YEARLY', ''),
    ('всеки 2 седмици', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('всеки 3 дни', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['петък', 'днес'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
