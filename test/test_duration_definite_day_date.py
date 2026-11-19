# -*- coding: utf-8 -*-
"""A definite article, a day word and a day number name a date, not a length."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

_DATES = [
    ("pt", "no dia 5 de dezembro"),
    ("pt", "o dia 25 de dezembro às 15h"),
    ("pt", "no dia cinco de dezembro"),
    ("es", "el día 5 de diciembre"),
    ("gl", "o día 5 de decembro"),
    ("ca", "el dia 5 de desembre"),
    ("fr", "le jour 5 décembre"),
    ("it", "il giorno 5 dicembre"),
    ("en", "the day 5 of december"),
]

_LENGTHS = [
    ("pt", "um dia", timedelta(days=1)),
    ("pt", "uma semana e um dia", timedelta(days=8)),
    ("pt", "durante o dia", timedelta(days=1)),
    ("es", "dura un día", timedelta(days=1)),
    ("pt", "2 dias", timedelta(days=2)),
]


@pytest.mark.parametrize("lang,text", _DATES)
def test_definite_day_number_is_no_duration(lang, text):
    assert extract_duration(text, lang) is None


@pytest.mark.parametrize("lang,text,expected", _LENGTHS)
def test_day_length_stays_a_duration(lang, text, expected):
    got = extract_duration(text, lang)
    assert got is not None and got.duration == expected
