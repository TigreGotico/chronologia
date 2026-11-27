# -*- coding: utf-8 -*-
"""A length beside a word that is no count of it.

"this year" or "every year" next to "eight days" is a deictic, not a stranded
calendar count, so it does not block the length.  A definite article before a
unit ("non vedo l'ora", I cannot wait) counts one only when the text names no
other length.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

_LENGTHS = [
    ("pt-PT", "O festival de música da aldeia dura oito dias e, este ano, "
              "promete encher as ruas de gente.", timedelta(days=8)),
    ("es", "El festival de cine de nuestro pueblo dura cinco días y cada año "
           "atrae a más visitantes.", timedelta(days=5)),
    ("fr", "Le festival de jazz du village dure deux jours, et chaque année "
           "les habitants ouvrent leurs jardins.", timedelta(days=2)),
    ("de", "Das Musikfestival am See dauert dieses Jahr acht Tage.",
     timedelta(days=8)),
    ("nl", "Het muziekfestival in het park duurt dit jaar tien dagen, dus "
           "neem gerust je tent mee.", timedelta(days=10)),
    ("nl", "Het muziekfestival duurt dit jaar maar liefst acht dagen.",
     timedelta(days=8)),
    ("it", "Il corso di ceramica dura dodici giorni, e non vedo l'ora di "
           "sporcarmi le mani.", timedelta(days=12)),
    ("it", "dura l'ora intera", timedelta(hours=1)),
    ("en", "the hour", timedelta(hours=1)),
]

_NO_LENGTH = [
    ("en", "3 months and 2 days"),
    ("en", "a month and 2 days"),
    ("pt-PT", "um ano e dois dias"),
    ("de", "ein Jahr und zwei Tage"),
]


@pytest.mark.parametrize("lang,text,expected", _LENGTHS)
def test_length_beside_deictic(lang, text, expected):
    got = extract_duration(text, lang)
    assert got is not None and got.duration == expected


@pytest.mark.parametrize("lang,text", _NO_LENGTH)
def test_counted_calendar_unit_still_refuses_without_anchor(lang, text):
    assert extract_duration(text, lang) is None
