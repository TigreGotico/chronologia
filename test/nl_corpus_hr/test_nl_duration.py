# -*- coding: utf-8 -*-
"""Durations in hr: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "hr"

_CASES = [
    ('5 minuta', timedelta(minutes=5)),
    ('45 minuta', timedelta(minutes=45)),
    ('2 sata', timedelta(hours=2)),
    ('1 sat', timedelta(hours=1)),
    ('2 dana', timedelta(days=2)),
    ('3 tjedna', timedelta(weeks=3)),
    ('90 minuta', timedelta(minutes=90)),
    ('pola sata', timedelta(minutes=30)),
    ('četvrt sata', timedelta(minutes=15)),
    ('2 dana 4 sata', timedelta(days=2, hours=4)),
    ('1 sat 30 minuta', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 lipnja', 'ništa vremensko ovdje'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
