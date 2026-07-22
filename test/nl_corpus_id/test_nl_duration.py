# -*- coding: utf-8 -*-
"""Durations in id: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "id"

_CASES = [
    ('5 menit', timedelta(minutes=5)),
    ('45 menit', timedelta(minutes=45)),
    ('2 jam', timedelta(hours=2)),
    ('1 jam', timedelta(hours=1)),
    ('2 hari', timedelta(days=2)),
    ('3 minggu', timedelta(weeks=3)),
    ('90 menit', timedelta(minutes=90)),
    ('setengah jam', timedelta(minutes=30)),
    ('seperempat jam', timedelta(minutes=15)),
    ('2 hari 4 jam', timedelta(days=2, hours=4)),
    ('1 jam 30 menit', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juni', 'tidak ada waktu di sini'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
