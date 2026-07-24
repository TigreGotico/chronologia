# -*- coding: utf-8 -*-
"""The terminative ``-ig`` durative in Hungarian: ``extract_duration``.

The terminative case names how long an action lasts -- "itt leszek két hétig"
(I will be here for two weeks) -- and it is the primary way a Hungarian speaker
states a duration, ahead of the accusative the corpus already exercised.  The
suffix is invariant: it is one of the few Hungarian endings with no
vowel-harmony alternation, so every unit simply takes ``-ig`` (any stem
lengthening -- ``óra`` -> ``óráig`` -- belongs to the noun, not the suffix).
See HungarianReference.com, "Terminative case: -ig".
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "hu"

# Only the fixed-width units (minute / hour / day / week) resolve to a
# timedelta; month and year are calendar-ambiguous and second is outside the
# duration engine's unit set, exactly as their accusative forms are.
_CASES = [
    ('egy hétig', timedelta(weeks=1)),
    ('három hétig', timedelta(weeks=3)),
    ('öt napig', timedelta(days=5)),
    ('két napig', timedelta(days=2)),
    ('két óráig', timedelta(hours=2)),
    ('kilenc óráig', timedelta(hours=9)),
    ('tíz percig', timedelta(minutes=10)),
    ('90 percig', timedelta(minutes=90)),
    ('3 hétig', timedelta(weeks=3)),
    ('2 napig 4 óráig', timedelta(days=2, hours=4)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_terminative_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 június', 'semmi időbeli itt', 'ig'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
