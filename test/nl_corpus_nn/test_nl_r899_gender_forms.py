# -*- coding: utf-8 -*-
"""GH-899 (nn): "one and a half" fuses into one word inflected for the
gender of the following noun. Nynorsk declares only "halvannan"
(masculine); the feminine form "halvanna" and the neuter form
"halvtanna" must resolve too, not refuse with None.

Source: English Wiktionary, "halvanna"
<https://en.wiktionary.org/wiki/halvanna>, Norwegian Nynorsk numeral,
"one and a half", feminine; lists masculine halvannan and neuter
halvtanna.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "nn"


def test_feminine_halvanna_veke():
    got = extract_duration("halvanna veke", LANG)
    assert got is not None
    assert got.duration == timedelta(days=10, hours=12)
    assert got.remainder.strip() == ""


def test_neuter_halvtanna_minutt():
    got = extract_duration("halvtanna minutt", LANG)
    assert got is not None
    assert got.duration == timedelta(seconds=90)
    assert got.remainder.strip() == ""


def test_already_declared_halvannan_still_resolves():
    got = extract_duration("halvannan time", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""
