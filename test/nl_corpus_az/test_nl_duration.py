# -*- coding: utf-8 -*-
"""Durations in az: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "az"

_CASES = [
    ('5 dəqiqə', timedelta(minutes=5)),
    ('45 dəqiqə', timedelta(minutes=45)),
    ('2 saat', timedelta(hours=2)),
    ('1 saat', timedelta(hours=1)),
    ('2 gün', timedelta(days=2)),
    ('3 həftə', timedelta(weeks=3)),
    ('90 dəqiqə', timedelta(minutes=90)),
    ('yarım saat', timedelta(minutes=30)),
    ('rüb saat', timedelta(minutes=15)),
    ('2 gün 4 saat', timedelta(days=2, hours=4)),
    ('1 saat 30 dəqiqə', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 iyun', 'burada vaxt yoxdur'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
