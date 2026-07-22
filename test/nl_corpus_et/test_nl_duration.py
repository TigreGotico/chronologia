# -*- coding: utf-8 -*-
"""Durations in et: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "et"

_CASES = [
    ('5 minutit', timedelta(minutes=5)),
    ('45 minutit', timedelta(minutes=45)),
    ('2 tundi', timedelta(hours=2)),
    ('1 tund', timedelta(hours=1)),
    ('2 päeva', timedelta(days=2)),
    ('3 nädalat', timedelta(weeks=3)),
    ('90 minutit', timedelta(minutes=90)),
    ('pool tund', timedelta(minutes=30)),
    ('veerand tund', timedelta(minutes=15)),
    ('2 päeva 4 tundi', timedelta(days=2, hours=4)),
    ('1 tund 30 minutit', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juuni', 'ei midagi ajalist siin'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
