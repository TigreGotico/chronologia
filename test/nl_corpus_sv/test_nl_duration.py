# -*- coding: utf-8 -*-
"""Durations in sv: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "sv"

_CASES = [
    ('5 minuter', timedelta(minutes=5)),
    ('45 minuter', timedelta(minutes=45)),
    ('2 timmar', timedelta(hours=2)),
    ('en timme', timedelta(hours=1)),
    ('2 dagar', timedelta(days=2)),
    ('3 veckor', timedelta(weeks=3)),
    ('90 minuter', timedelta(minutes=90)),
    ('halv timme', timedelta(minutes=30)),
    ('en kvart timme', timedelta(minutes=15)),
    ('2 dagar 4 timmar', timedelta(days=2, hours=4)),
    ('1 timmar 30 minuter', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juni', 'inget tidsligt här'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
