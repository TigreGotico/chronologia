# -*- coding: utf-8 -*-
"""Durations in fi: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fi"

_CASES = [
    ('5 minuuttia', timedelta(minutes=5)),
    ('45 minuuttia', timedelta(minutes=45)),
    ('2 tuntia', timedelta(hours=2)),
    ('1 tunti', timedelta(hours=1)),
    ('2 päivää', timedelta(days=2)),
    ('3 viikkoa', timedelta(weeks=3)),
    ('90 minuuttia', timedelta(minutes=90)),
    ('puoli tunti', timedelta(minutes=30)),
    ('vartti tunti', timedelta(minutes=15)),
    ('2 päivää 4 tuntia', timedelta(days=2, hours=4)),
    ('1 tunti 30 minuuttia', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 kesäkuuta', 'ei mitään ajallista tässä'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
