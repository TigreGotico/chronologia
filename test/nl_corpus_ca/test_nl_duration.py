# -*- coding: utf-8 -*-
"""Durations in ca: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ca"

_CASES = [
    ('5 minuts', timedelta(minutes=5)),
    ('45 minuts', timedelta(minutes=45)),
    ('2 hora', timedelta(hours=2)),
    ('una hora', timedelta(hours=1)),
    ('un dies', timedelta(days=1)),
    ('2 dies', timedelta(days=2)),
    ('3 setmanes', timedelta(weeks=3)),
    ('90 minuts', timedelta(minutes=90)),
    ('mitja hora', timedelta(minutes=30)),
    ('un quart de hora', timedelta(minutes=15)),
    ('2 dies 4 hora', timedelta(days=2, hours=4)),
    ('1 hora 30 minuts', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 mesos', 'res aquí'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
