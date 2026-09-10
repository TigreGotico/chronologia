# -*- coding: utf-8 -*-
"""GH-899 (nb): "one and a half" fuses into one word inflected for the
gender of the following noun. Bokmal declares only "halvannen"
(masculine and feminine); the neuter form "halvannet" and the
feminine variant "halvanna" must resolve too, not refuse with None.

Source: English Wiktionary, "halvannet"
<https://en.wiktionary.org/wiki/halvannet>, Norwegian Bokmal determiner,
"one and a half" (neuter form); alternative forms halvanna (feminine),
halvannen (masculine and feminine); cites The Bokmal Dictionary.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "nb"


def test_neuter_halvannet_minutt():
    got = extract_duration("halvannet minutt", LANG)
    assert got is not None
    assert got.duration == timedelta(seconds=90)
    assert got.remainder.strip() == ""


def test_feminine_halvanna_control():
    got = extract_duration("halvanna time", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_already_declared_halvannen_still_resolves():
    got = extract_duration("halvannen time", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""
