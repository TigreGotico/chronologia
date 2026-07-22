# -*- coding: utf-8 -*-
"""Durations in fy: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fy"

_CASES = [
    ('5 minuten', timedelta(minutes=5)),
    ('45 minuten', timedelta(minutes=45)),
    ('2 oeren', timedelta(hours=2)),
    ('in oere', timedelta(hours=1)),
    ('2 dagen', timedelta(days=2)),
    ('3 wiken', timedelta(weeks=3)),
    ('90 minuten', timedelta(minutes=90)),
    ('heal oere', timedelta(minutes=30)),
    ('in kwart oere', timedelta(minutes=15)),
    ('2 dagen 4 oeren', timedelta(days=2, hours=4)),
    ('1 oeren 30 minuten', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juny', 'neat temporeels hjir'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
