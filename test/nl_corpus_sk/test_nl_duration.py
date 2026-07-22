# -*- coding: utf-8 -*-
"""Durations in sk: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "sk"

_CASES = [
    ('5 minút', timedelta(minutes=5)),
    ('45 minút', timedelta(minutes=45)),
    ('2 hodiny', timedelta(hours=2)),
    ('1 hodina', timedelta(hours=1)),
    ('2 dni', timedelta(days=2)),
    ('3 týždne', timedelta(weeks=3)),
    ('90 minút', timedelta(minutes=90)),
    ('pol hodiny', timedelta(minutes=30)),
    ('štvrť hodiny', timedelta(minutes=15)),
    ('2 dni 4 hodiny', timedelta(days=2, hours=4)),
    ('1 hodina 30 minút', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 júna', 'nič časové tu'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
