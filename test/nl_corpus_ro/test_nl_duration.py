# -*- coding: utf-8 -*-
"""Durations in ro: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ro"

_CASES = [
    ('5 minute', timedelta(minutes=5)),
    ('45 minute', timedelta(minutes=45)),
    ('2 ore', timedelta(hours=2)),
    ('o ore', timedelta(hours=1)),
    ('un zile', timedelta(days=1)),
    ('2 zile', timedelta(days=2)),
    ('3 săptămâni', timedelta(weeks=3)),
    ('90 minute', timedelta(minutes=90)),
    ('jumătate ore', timedelta(minutes=30)),
    ('un sfert de ore', timedelta(minutes=15)),
    ('2 zile 4 ore', timedelta(days=2, hours=4)),
    ('1 ore 30 minute', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 luni', 'nimic aici'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
