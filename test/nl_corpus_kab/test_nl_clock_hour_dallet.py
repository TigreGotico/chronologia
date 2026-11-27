# -*- coding: utf-8 -*-
"""Kabyle clock hours as Dallet writes them: the bare hour, often after "d".

Source: J.-M. Dallet, Dictionnaire kabyle-français, parler des At Mangellat
(SELAF, Paris, 1982).  The page of each hour form is beside its row.  The
forms with the article vowel ("ezzuj", "elxemsa", "eɛecṛa") are Dallet's own
clock examples: "d ezzuj" p. 938, "d elxemsa" p. 902, "d eɛecṛa ɣir ɛecrin,
il est 10 heures moins 20" p. 634.

Anchor Tuesday 2017-06-27 13:04.  Gold is worked out by hand from the anchor:
a pm or night hour still ahead today lands on 06-27, a morning hour on 06-28.
A lone hour with no day part takes the next twelve-hour reading (ruling 17).
"""
from datetime import datetime

import pytest

from ._corpus import parse

A = datetime(2017, 6, 27, 13, 4)

_HOURS = [
    ("ɣef juj n tmeddit", (2017, 6, 27, 14, 0)),       # p. 357
    ("ɣef zuj n tmeddit", (2017, 6, 27, 14, 0)),       # p. 938
    ("ɣef zzuj n tmeddit", (2017, 6, 27, 14, 0)),      # p. 938
    ("d ezzuj n tmeddit", (2017, 6, 27, 14, 0)),       # p. 938
    ("d elxemsa n tmeddit", (2017, 6, 27, 17, 0)),     # p. 902
    ("ɣef sett n tmeddit", (2017, 6, 27, 18, 0)),      # p. 793
    ("ɣef essebɛa n tmeddit", (2017, 6, 27, 19, 0)),   # p. 756
    ("d eɛecṛa n tmeddit", (2017, 6, 27, 22, 0)),      # p. 634
    ("ɣef eḥdac n tmeddit", (2017, 6, 27, 23, 0)),     # p. 305
    ("ɣef eḥdac n yiḍ", (2017, 6, 27, 23, 0)),         # p. 305
    ("ɣef eṭṭnac n uzal", (2017, 6, 28, 12, 0)),       # p. 826
    # "ɣir", "moins (dans le compte des heures)", p. 634: 10 minus 20.
    ("d eɛecṛa ɣir ɛecrin n tṣebḥit", (2017, 6, 28, 9, 40)),
    ("d eɛecṛa ɣir ɛecrin", (2017, 6, 27, 21, 40)),
]


@pytest.mark.parametrize("text,want", _HOURS)
def test_dallet_clock_hour(text, want):
    r = parse(text, A)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want
    assert r[1] == "", "%r stranded %r" % (text, r[1])


# Bench twins from the date benches.  The first row is verbatim; the other
# two put "ass-a" (today) in place of a day offset the parser does not read.
@pytest.mark.parametrize("text,want", [
    ("Tiddukla n taddart ad temlil ass-a ɣef eḥdac n yiḍ deg uxxam n yilmeẓyen.",
     (2017, 6, 27, 23, 0)),
    ("Tamesrit n tmaziɣt ad teldi tiwwura-s ass-a, ɣef zzuj n tmeddit.",
     (2017, 6, 27, 14, 0)),
    ("Ahil n tmuzikt ad yebdu ass-a, ɣef essebɛa n tmeddit.",
     (2017, 6, 27, 19, 0)),
])
def test_dallet_clock_in_a_sentence(text, want):
    r = parse(text, A)
    assert r is not None, "%r did not parse" % text
    s = r[0].start
    assert (s.year, s.month, s.day, s.hour, s.minute) == want
