# -*- coding: utf-8 -*-
"""The Finnish numeral ``puolitoista`` ("one and a half").

Source: Wiktionary, `puolitoista <https://en.wiktionary.org/wiki/puolitoista>`_,
fetched and read -- Finnish numeral, "one and a half", with *puolitoista tuntia*
= "an hour and a half" as its own usage example.  That page names Kielitoimiston
sanakirja as further reading; the dictionary itself was not fetched.

The genitive *puolentoista* is read already; the citation form is what a speaker
writes in front of a partitive unit.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fi"

_CASES = [
    ('puolitoista tuntia', timedelta(minutes=90)),
    ('puolitoista minuuttia', timedelta(seconds=90)),
    ('puolitoista päivää', timedelta(days=1, hours=12)),
    ('puolitoista viikkoa', timedelta(days=10, hours=12)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_puolitoista_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,expected", [
    ('puolentoista tunnin', timedelta(minutes=90)),
    ('puoli tuntia', timedelta(minutes=30)),
    ('kaksi ja puoli tuntia', timedelta(minutes=150)),
])
def test_neighbouring_halves_unchanged(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


def test_bare_numeral_is_not_a_duration():
    assert extract_duration('puolitoista', LANG) is None
