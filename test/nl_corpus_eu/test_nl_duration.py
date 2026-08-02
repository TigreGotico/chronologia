# -*- coding: utf-8 -*-
"""Durations in eu: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "eu"

_CASES = [
    ('5 minutu', timedelta(minutes=5)),
    ('45 minutu', timedelta(minutes=45)),
    ('2 ordu', timedelta(hours=2)),
    ('1 ordu', timedelta(hours=1)),
    ('2 egun', timedelta(days=2)),
    ('3 aste', timedelta(weeks=3)),
    ('90 minutu', timedelta(minutes=90)),
    ('erdi ordu', timedelta(minutes=30)),
    ('laurden ordu', timedelta(minutes=15)),
    ('2 egun 4 ordu', timedelta(days=2, hours=4)),
    ('1 ordu 30 minutu', timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 ekainaren', 'ezer denborazkorik hemen'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


@pytest.mark.parametrize("text,expected", [
    ('berrehun egun', timedelta(days=200)),
    ('hirurehun egun', timedelta(days=300)),
    ('bostehun egun', timedelta(days=500)),
])
def test_duration_spelled_hundreds(text, expected):
    # Single-token Basque hundreds fold; the compound connector "eta" is excluded
    # from the number set so the spoken clock ("bostak eta erdi") still resolves.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
