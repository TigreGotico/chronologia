# -*- coding: utf-8 -*-
"""Durations in uk: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "uk"

_CASES = [
    ('5 хвилин', timedelta(minutes=5)),
    ('45 хвилин', timedelta(minutes=45)),
    ('2 години', timedelta(hours=2)),
    ('1 година', timedelta(hours=1)),
    ('2 дні', timedelta(days=2)),
    ('3 тижні', timedelta(weeks=3)),
    ('90 хвилин', timedelta(minutes=90)),
    ('пів години', timedelta(minutes=30)),
    ('чверть години', timedelta(minutes=15)),
    ('2 дні 4 години', timedelta(days=2, hours=4)),
    ('1 година 30 хвилин', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 червня', 'нічого часового тут'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
