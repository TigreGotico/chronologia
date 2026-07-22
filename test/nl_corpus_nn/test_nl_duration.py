# -*- coding: utf-8 -*-
"""Durations in nn: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "nn"

_CASES = [
    ('5 minutta', timedelta(minutes=5)),
    ('45 minutta', timedelta(minutes=45)),
    ('2 timar', timedelta(hours=2)),
    ('ein time', timedelta(hours=1)),
    ('2 dagar', timedelta(days=2)),
    ('3 veker', timedelta(weeks=3)),
    ('90 minutta', timedelta(minutes=90)),
    ('halv time', timedelta(minutes=30)),
    ('ein fjerdedel time', timedelta(minutes=15)),
    ('2 dagar 4 timar', timedelta(days=2, hours=4)),
    ('1 timar 30 minutta', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juni', 'ingenting tidsmessig her'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
