# -*- coding: utf-8 -*-
"""Recurrence in et: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "et"

_CASES = [
    ('iga reede', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('iga esmaspäev', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('iga päev', 'FREQ=DAILY', ''),
    ('iga nädal', 'FREQ=WEEKLY', ''),
    ('iga kuu', 'FREQ=MONTHLY', ''),
    ('iga aasta', 'FREQ=YEARLY', ''),
    ('iga 2 nädal', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('iga 3 päev', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['reede', 'täna'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
