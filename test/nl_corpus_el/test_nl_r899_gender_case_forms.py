# -*- coding: utf-8 -*-
"""R899 (el): "one and a half" fuses into a single word that agrees in
gender with the following noun. "μιάμιση" (feminine, agreeing with
feminine "ώρα", hour) is declared already and is exercised by R133.
"λεπτό" (minute) is neuter and needs the neuter form "ενάμισι".

Source: Greek Wiktionary, `μιάμιση
<https://el.wiktionary.org/wiki/%CE%BC%CE%B9%CE%AC%CE%BC%CE%B9%CF%83%CE%B7>`_,
fetched and read -- Αριθμητικό (numeral) glossed "μία και μισή" (one and a
half), marked "(θηλυκό του ενάμισης)" (feminine of "ενάμισης"). The set
given is "ενάμισης" (masculine) / "ενάμισι" (neuter) / "μιάμιση"
(feminine).

Only the neuter "ενάμισι" gets a reproduction here, because only "λεπτό"
(minute) is a supported neuter unit. The masculine "ενάμισης" is left out:
no supported unit in this engine is grammatically masculine, so there is
no phrase to isolate it and no reproduction to prove it works.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "el"


def test_fused_enamisi_neuter_minute_idiom():
    got = extract_duration("ενάμισι λεπτό", LANG)
    assert got is not None
    assert got.duration == timedelta(seconds=90)
    assert got.remainder.strip() == ""


def test_declared_miamisi_control_still_resolves():
    got = extract_duration("μιάμιση ώρα", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""
