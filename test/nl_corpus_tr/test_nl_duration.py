# -*- coding: utf-8 -*-
"""Durations in tr: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "tr"

_CASES = [
    ('5 dakika', timedelta(minutes=5)),
    ('45 dakika', timedelta(minutes=45)),
    ('2 saat', timedelta(hours=2)),
    ('1 saat', timedelta(hours=1)),
    ('2 gün', timedelta(days=2)),
    ('3 hafta', timedelta(weeks=3)),
    ('90 dakika', timedelta(minutes=90)),
    ('yarım saat', timedelta(minutes=30)),
    ('çeyrek saat', timedelta(minutes=15)),
    ('2 gün 4 saat', timedelta(days=2, hours=4)),
    ('1 saat 30 dakika', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 haziran', 'burada zamansal bir şey yok'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
