# -*- coding: utf-8 -*-
"""Recurrence in ru: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ru"

_CASES = [
    ('каждую пятницу', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('каждый понедельник', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('ежедневно', 'FREQ=DAILY', ''),
    ('еженедельно', 'FREQ=WEEKLY', ''),
    ('ежемесячно', 'FREQ=MONTHLY', ''),
    ('ежегодно', 'FREQ=YEARLY', ''),
    ('каждые 2 недели', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('каждые 3 дня', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['пятницу', 'сегодня'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
