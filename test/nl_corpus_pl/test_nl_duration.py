# -*- coding: utf-8 -*-
"""Durations in pl: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "pl"

_CASES = [
    ('5 minut', timedelta(minutes=5)),
    ('45 minut', timedelta(minutes=45)),
    ('2 godziny', timedelta(hours=2)),
    ('1 godzina', timedelta(hours=1)),
    ('2 dni', timedelta(days=2)),
    ('3 tygodnie', timedelta(weeks=3)),
    ('90 minut', timedelta(minutes=90)),
    ('pół godziny', timedelta(minutes=30)),
    ('ćwierć godziny', timedelta(minutes=15)),
    ('2 dni 4 godziny', timedelta(days=2, hours=4)),
    ('1 godzina 30 minut', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 czerwca', 'nic czasowego tutaj'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
