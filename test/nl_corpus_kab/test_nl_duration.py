# -*- coding: utf-8 -*-
"""Durations in kab: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "kab"

_CASES = [
    ('5 tesdidin', timedelta(minutes=5)),
    ('45 tesdidin', timedelta(minutes=45)),
    ('2 ssaɛa', timedelta(hours=2)),
    ('1 ssaɛa', timedelta(hours=1)),
    ('2 ass', timedelta(days=2)),
    ('3 imalasen', timedelta(weeks=3)),
    ('90 tesdidin', timedelta(minutes=90)),
    ('azgen ssaɛa', timedelta(minutes=30)),
    ('rrbeɛ ssaɛa', timedelta(minutes=15)),
    ('2 ass 4 ssaɛa', timedelta(days=2, hours=4)),
    ('1 ssaɛa 30 tesdidin', timedelta(hours=1, minutes=30)),
    # Spelled teens, read through numtag since 0.46.0a2 (numtag#404): "mraw d
    # yiwen" is 10 + 1 and "mraw d sin" is 10 + 2 in numtag's kab lexicon
    # (mraw, yiwen and sin each carry a source there). Formerly #1210.
    ('mraw d yiwen n tesdidin', timedelta(minutes=11)),
    ('mraw d sin n tesdidin', timedelta(minutes=12)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 yunyu', 'ulac akud dagi'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
