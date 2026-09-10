# -*- coding: utf-8 -*-
"""R899 (cs): "one and a half" fuses into a single word that inflects for
the gender and case of the following noun. "půldruhé" (neuter, agreeing
with feminine genitive-declined nouns via the older mixed paradigm) is
declared already and is exercised by R133. "dne" (genitive singular of
"den", day) needs the masculine genitive singular form "půldruhého".

Source: Czech Wiktionary, `půldruhý
<https://cs.wiktionary.org/wiki/p%C5%AFldruh%C3%BD>`_, fetched and read --
čislovka (numeral) glossed "mající hodnotu jeden a půl (uvedených
jednotek)". Its declension table gives masculine animate/inanimate
nominative singular "půldruhý", feminine nominative singular "půldruhá",
neuter nominative singular "půldruhé", masculine genitive singular
"půldruhého", feminine genitive singular "půldruhé", neuter genitive
singular "půldruhého".

Only the genitive masculine "půldruhého" gets a reproduction here, because
only "dne" (genitive singular of "day") is a supported unit that isolates
it. The nominative forms in the table are not added: nothing in the
supported unit list needs them, and an untested form would make the
parser permissive without evidence.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "cs"


def test_fused_puldruheho_genitive_day_idiom():
    got = extract_duration("půldruhého dne", LANG)
    assert got is not None
    assert got.duration == timedelta(days=1, hours=12)
    assert got.remainder.strip() == ""


def test_declared_puldruhe_control_still_resolves():
    got = extract_duration("půldruhé hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""
