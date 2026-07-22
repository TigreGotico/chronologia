# -*- coding: utf-8 -*-
"""Durations in fa: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fa"

_CASES = [
    ('5 دقیقه', timedelta(minutes=5)),
    ('45 دقیقه', timedelta(minutes=45)),
    ('2 ساعت', timedelta(hours=2)),
    ('1 ساعت', timedelta(hours=1)),
    ('2 روز', timedelta(days=2)),
    ('3 هفته', timedelta(weeks=3)),
    ('90 دقیقه', timedelta(minutes=90)),
    ('نیم ساعت', timedelta(minutes=30)),
    ('ربع ساعت', timedelta(minutes=15)),
    ('2 روز 4 ساعت', timedelta(days=2, hours=4)),
    ('1 ساعت 30 دقیقه', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 ژوئن', 'اینجا چیز زمانی نیست'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
