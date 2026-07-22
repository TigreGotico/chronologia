# -*- coding: utf-8 -*-
"""Durations in Portuguese: ``extract_duration(text, "pt")`` -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "pt"

_CASES = [
    ("5 minutos", timedelta(minutes=5)),
    ("1 minuto", timedelta(minutes=1)),
    ("2 horas", timedelta(hours=2)),
    ("uma hora", timedelta(hours=1)),
    ("4 horas", timedelta(hours=4)),
    ("um dia", timedelta(days=1)),
    ("2 dias", timedelta(days=2)),
    ("3 semanas", timedelta(weeks=3)),
    ("noventa minutos", timedelta(minutes=90)),
    ("meia hora", timedelta(minutes=30)),
    ("um quarto de hora", timedelta(minutes=15)),
    ("três quartos de hora", timedelta(minutes=45)),
    ("uma hora e meia", timedelta(hours=1, minutes=30)),
    ("duas horas e meia", timedelta(hours=2, minutes=30)),
    ("2 dias 4 horas", timedelta(days=2, hours=4)),
    ("1 hora 30 minutos", timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ["2 meses", "ola mundo"])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
