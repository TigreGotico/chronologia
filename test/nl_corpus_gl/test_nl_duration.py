# -*- coding: utf-8 -*-
"""Durations in gl: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "gl"

_CASES = [
    ('5 minutos', timedelta(minutes=5)),
    ('45 minutos', timedelta(minutes=45)),
    ('2 hora', timedelta(hours=2)),
    ('unha hora', timedelta(hours=1)),
    ('un días', timedelta(days=1)),
    ('2 días', timedelta(days=2)),
    ('3 semanas', timedelta(weeks=3)),
    ('90 minutos', timedelta(minutes=90)),
    ('media hora', timedelta(minutes=30)),
    ('un cuarto de hora', timedelta(minutes=15)),
    ('2 días 4 hora', timedelta(days=2, hours=4)),
    ('1 hora 30 minutos', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 meses', 'nada aquí'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
