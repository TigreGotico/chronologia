# -*- coding: utf-8 -*-
"""Durations in ru: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ru"

_CASES = [
    ('5 минут', timedelta(minutes=5)),
    ('45 минут', timedelta(minutes=45)),
    ('2 часа', timedelta(hours=2)),
    ('1 час', timedelta(hours=1)),
    ('2 дня', timedelta(days=2)),
    ('3 недели', timedelta(weeks=3)),
    ('90 минут', timedelta(minutes=90)),
    ('пол часа', timedelta(minutes=30)),
    ('четверть часа', timedelta(minutes=15)),
    ('2 дня 4 часа', timedelta(days=2, hours=4)),
    ('1 час 30 минут', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 июня', 'ничего временного здесь'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
