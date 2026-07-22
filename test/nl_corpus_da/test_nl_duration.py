# -*- coding: utf-8 -*-
"""Durations in da: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "da"

_CASES = [
    ('5 minutter', timedelta(minutes=5)),
    ('45 minutter', timedelta(minutes=45)),
    ('2 timer', timedelta(hours=2)),
    ('en time', timedelta(hours=1)),
    ('2 dage', timedelta(days=2)),
    ('3 uger', timedelta(weeks=3)),
    ('90 minutter', timedelta(minutes=90)),
    ('halv time', timedelta(minutes=30)),
    ('en kvart time', timedelta(minutes=15)),
    ('2 dage 4 timer', timedelta(days=2, hours=4)),
    ('1 timer 30 minutter', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 juni', 'intet tidsligt her'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
