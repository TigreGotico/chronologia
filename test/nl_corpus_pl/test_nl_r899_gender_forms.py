# -*- coding: utf-8 -*-
"""GH-899 (pl): "one and a half" fuses into one word inflected for the
gender of the following noun. Polish declares only "półtorej"
(feminine); the masculine/neuter form "półtora" must resolve too,
not refuse with None.

Source: English Wiktionary, "półtora"
<https://en.wiktionary.org/wiki/p%C3%B3%C5%82tora>, Polish numeral,
"one and a half", used with masculine or neuter; derived term
półtorej; cites Wielki słownik języka polskiego (IJP PAN), wsjp.pl.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "pl"


def test_masc_neuter_poltora_dnia():
    got = extract_duration("półtora dnia", LANG)
    assert got is not None
    assert got.duration == timedelta(days=1, hours=12)
    assert got.remainder.strip() == ""


def test_masc_neuter_poltora_tygodnia():
    got = extract_duration("półtora tygodnia", LANG)
    assert got is not None
    assert got.duration == timedelta(days=10, hours=12)
    assert got.remainder.strip() == ""


def test_already_declared_poltorej_still_resolves():
    got = extract_duration("półtorej godziny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""
