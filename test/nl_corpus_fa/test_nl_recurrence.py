# -*- coding: utf-8 -*-
"""Recurrence in fa: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fa"

_CASES = [
    ('هر جمعه', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('هر دوشنبه', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('روزانه', 'FREQ=DAILY', ''),
    ('هفتگی', 'FREQ=WEEKLY', ''),
    ('ماهانه', 'FREQ=MONTHLY', ''),
    ('سالانه', 'FREQ=YEARLY', ''),
    ('هر 2 هفته', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('هر 3 روز', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['جمعه', 'امروز'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
