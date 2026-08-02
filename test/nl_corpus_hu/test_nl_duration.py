# -*- coding: utf-8 -*-
"""Durations in hu: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "hu"

_CASES = [
    ('5 percet', timedelta(minutes=5)),
    ('45 percet', timedelta(minutes=45)),
    ('2 órát', timedelta(hours=2)),
    ('1 óra', timedelta(hours=1)),
    ('2 napot', timedelta(days=2)),
    ('3 hetet', timedelta(weeks=3)),
    ('90 percet', timedelta(minutes=90)),
    ('fél óra', timedelta(minutes=30)),
    ('negyed óra', timedelta(minutes=15)),
    ('2 napot 4 órát', timedelta(days=2, hours=4)),
    ('1 óra 30 percet', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 június', 'semmi időbeli itt'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


@pytest.mark.parametrize("text,expected", [
    ('kétszáz nap', timedelta(days=200)),
    ('ötszáz nap', timedelta(days=500)),
])
def test_duration_spelled_hundreds(text, expected):
    # The model-derived run set was built 0..100, so single-token hundred words
    # (kétszáz=200) never folded and returned None. The 0..999 sweep admits them.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
