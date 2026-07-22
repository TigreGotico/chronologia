# -*- coding: utf-8 -*-
"""Durations in cs: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "cs"

_CASES = [
    ('5 minut', timedelta(minutes=5)),
    ('45 minut', timedelta(minutes=45)),
    ('2 hodiny', timedelta(hours=2)),
    ('1 hodina', timedelta(hours=1)),
    ('2 dny', timedelta(days=2)),
    ('3 týdny', timedelta(weeks=3)),
    ('90 minut', timedelta(minutes=90)),
    ('půl hodiny', timedelta(minutes=30)),
    ('čtvrt hodiny', timedelta(minutes=15)),
    ('2 dny 4 hodiny', timedelta(days=2, hours=4)),
    ('1 hodina 30 minut', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 června', 'nic časového tady'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
