# -*- coding: utf-8 -*-
"""Durations in sl: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "sl"

_CASES = [
    ('5 minut', timedelta(minutes=5)),
    ('45 minut', timedelta(minutes=45)),
    ('2 ure', timedelta(hours=2)),
    ('1 ura', timedelta(hours=1)),
    ('2 dni', timedelta(days=2)),
    ('3 tedne', timedelta(weeks=3)),
    ('90 minut', timedelta(minutes=90)),
    ('pol ure', timedelta(minutes=30)),
    ('četrt ure', timedelta(minutes=15)),
    ('2 dni 4 ure', timedelta(days=2, hours=4)),
    ('1 ura 30 minut', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 junija', 'nič časovnega tukaj'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
