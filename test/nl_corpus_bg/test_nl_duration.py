# -*- coding: utf-8 -*-
"""Durations in bg: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "bg"

_CASES = [
    ('5 минути', timedelta(minutes=5)),
    ('45 минути', timedelta(minutes=45)),
    ('2 часа', timedelta(hours=2)),
    ('1 час', timedelta(hours=1)),
    ('2 дни', timedelta(days=2)),
    ('3 седмици', timedelta(weeks=3)),
    ('90 минути', timedelta(minutes=90)),
    ('половин час', timedelta(minutes=30)),
    ('четвърт час', timedelta(minutes=15)),
    ('2 дни 4 часа', timedelta(days=2, hours=4)),
    ('1 час 30 минути', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 юни', 'нищо времево тук'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
