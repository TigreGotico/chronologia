# -*- coding: utf-8 -*-
"""Durations in ar: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ar"

_CASES = [
    ('5 دقائق', timedelta(minutes=5)),
    ('45 دقائق', timedelta(minutes=45)),
    ('2 ساعة', timedelta(hours=2)),
    ('1 ساعة', timedelta(hours=1)),
    ('2 يوم', timedelta(days=2)),
    ('3 أسبوع', timedelta(weeks=3)),
    ('90 دقائق', timedelta(minutes=90)),
    ('نصف ساعة', timedelta(minutes=30)),
    ('ربع ساعة', timedelta(minutes=15)),
    ('2 يوم 4 ساعة', timedelta(days=2, hours=4)),
    ('1 ساعة 30 دقائق', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 يونيو', 'لا شيء زمني هنا'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
