# -*- coding: utf-8 -*-
"""Kabyle date words in their ordinary sense, and "one morning" phrases.

tafsut (spring) is also a given name, lḥedd (Sunday) is also "limit", azal
(daytime) is also "value"; the Tatoeba ids are in marker_homograph.voc.
"yiwet n tṣebḥit" ("one morning") is indefinite and names no date; the
sources are in marker_indef_daypart.voc.  Anchor Tue 2017-06-27 13:04: the
next Sunday is 2017-07-02, the next 06:00 and 13:00 fall on 2017-06-28.
"""
from datetime import datetime

import pytest

from ._corpus import nomatch, start

NO_DATE = [
    "Tafsut tura tabrat i yemma-s yezdɣen di taddart.",
    "Tafsut tefka i yemma-s aqbuc n waman seg tala n taddart.",
    "Ula d ṣṣber yesɛa lḥedd, ihi ur t-ttɛeddi ara.",
    "Yal tayri ɣur-s lḥedd-is, ma tɛeddaḍ-t ad tesruḥeḍ ul.",
    "Leḥmala n yemma i warraw-is ur tesεi lḥedd.",
    "Azal n wexxam-agi yuli aṭas segmi d-bnan abrid amaynut.",
    "Awal ur nettwaḍfer s lefɛal ur yesɛi ara azal ɣer yemdanen.",
    "Yiwet n tṣebḥit n tegrest, nekker-d nufa adfel yeɣli-d.",
    "Yiwet tsebḥit n ccetwa, yeffeɣ jeddi ɣer tebḥirt.",
    "Deg yiwet n tṣebḥit n tegrest, yemma tessewwa-d aɣrum.",
    "Yiwet n tṣebḥit n tefsut, yemma tekker-d zik.",
]


@pytest.mark.parametrize("text", NO_DATE)
def test_ordinary_sense_names_no_date(text):
    nomatch(text)


DATED = [
    ("Ass n lḥedd ad nruḥ ɣer taddart.", datetime(2017, 7, 2)),
    ("lḥedd-agi ad nruḥ ɣer taddart.", datetime(2017, 7, 2)),
    ("Imekli yewjed-d ɣef yiwet n tmeddit.", datetime(2017, 6, 28, 13, 0)),
    ("Ttekkreɣ-d ɣef ssetta n tsebḥit.", datetime(2017, 6, 28, 6, 0)),
    ("ad nruḥ deg tafsut", datetime(2017, 3, 1)),
    ("Sem 20 Tub 2023 d ass n tmettant.", datetime(2023, 10, 20)),
    ("Nunembeṛ", datetime(2017, 11, 1)),
]


@pytest.mark.parametrize("text,gold", DATED)
def test_date_cue_keeps_the_date(text, gold):
    assert start(text) == gold
