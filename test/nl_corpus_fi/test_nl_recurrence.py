# -*- coding: utf-8 -*-
"""Recurrence in fi: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fi"

_CASES = [
    ('joka perjantai', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('joka maanantai', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('päivittäin', 'FREQ=DAILY', ''),
    ('viikoittain', 'FREQ=WEEKLY', ''),
    ('kuukausittain', 'FREQ=MONTHLY', ''),
    ('vuosittain', 'FREQ=YEARLY', ''),
    ('joka 2 viikko', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('joka 3 päivä', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['perjantai', 'tänään'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
