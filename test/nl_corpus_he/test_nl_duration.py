# -*- coding: utf-8 -*-
"""Durations in he: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "he"

_CASES = [
    ('5 דקות', timedelta(minutes=5)),
    ('45 דקות', timedelta(minutes=45)),
    ('2 שעה', timedelta(hours=2)),
    ('1 שעה', timedelta(hours=1)),
    ('2 ימים', timedelta(days=2)),
    ('3 שבועות', timedelta(weeks=3)),
    ('90 דקות', timedelta(minutes=90)),
    ('חצי שעה', timedelta(minutes=30)),
    ('רבע שעה', timedelta(minutes=15)),
    ('2 ימים 4 שעה', timedelta(days=2, hours=4)),
    ('1 שעה 30 דקות', timedelta(hours=1, minutes=30)),
    # dual-noun "two hours/days/weeks" fused into a single word (2 x unit)
    ('שעתיים ו-30 דקות', timedelta(hours=2, minutes=30)),
    ('שעתיים', timedelta(hours=2)),
    ('יומיים', timedelta(days=2)),
    ('שבועיים', timedelta(weeks=2)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 יוני', 'אין כאן שום דבר זמני'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


@pytest.mark.parametrize("text,expected", [
    ('שעתיים וחצי', timedelta(hours=2, minutes=30)),
    ('שעתיים ורבע', timedelta(hours=2, minutes=15)),
])
def test_duration_vav_fused_fraction(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
