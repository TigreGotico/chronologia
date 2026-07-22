# -*- coding: utf-8 -*-
"""Durations in ast: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ast"

_CASES = [
    ('5 minutos', timedelta(minutes=5)),
    ('45 minutos', timedelta(minutes=45)),
    ('2 hora', timedelta(hours=2)),
    ('una hora', timedelta(hours=1)),
    ('un díes', timedelta(days=1)),
    ('2 díes', timedelta(days=2)),
    ('3 selmanes', timedelta(weeks=3)),
    ('90 minutos', timedelta(minutes=90)),
    ('media hora', timedelta(minutes=30)),
    ('un cuartu de hora', timedelta(minutes=15)),
    ('2 díes 4 hora', timedelta(days=2, hours=4)),
    ('1 hora 30 minutos', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 meses', 'nada equí'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
