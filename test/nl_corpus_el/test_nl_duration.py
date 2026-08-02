# -*- coding: utf-8 -*-
"""Durations in el: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "el"

_CASES = [
    ('5 λεπτά', timedelta(minutes=5)),
    ('45 λεπτά', timedelta(minutes=45)),
    ('2 ώρες', timedelta(hours=2)),
    ('1 ώρα', timedelta(hours=1)),
    ('2 μέρες', timedelta(days=2)),
    ('3 εβδομάδες', timedelta(weeks=3)),
    ('90 λεπτά', timedelta(minutes=90)),
    ('μισή ώρα', timedelta(minutes=30)),
    ('τέταρτο ώρα', timedelta(minutes=15)),
    ('2 μέρες 4 ώρες', timedelta(days=2, hours=4)),
    ('1 ώρα 30 λεπτά', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 ιουνίου', 'τίποτα χρονικό εδώ'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


@pytest.mark.parametrize("text,expected", [
    ('διακόσιες μέρες', timedelta(days=200)),   # feminine hundreds (μέρα is fem.)
    ('πεντακόσιες μέρες', timedelta(days=500)),
    ('εννιακόσιες μέρες', timedelta(days=900)),
])
def test_duration_spelled_feminine_hundreds(text, expected):
    # pronounce_number_el emits only the neuter hundred; the feminine forms that
    # agree with feminine unit nouns folded to None until added to the run set.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
