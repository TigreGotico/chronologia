# -*- coding: utf-8 -*-
"""Durations in Spanish: ``extract_duration(text, "es")`` -> timedelta.

Fixed-width units only; expected values are hand-derived seconds arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "es"

_CASES = [
    ("5 minutos", timedelta(minutes=5)),
    ("1 minuto", timedelta(minutes=1)),
    ("45 minutos", timedelta(minutes=45)),
    ("2 horas", timedelta(hours=2)),
    ("una hora", timedelta(hours=1)),
    ("4 horas", timedelta(hours=4)),
    ("un dia", timedelta(days=1)),
    ("2 dias", timedelta(days=2)),
    ("3 semanas", timedelta(weeks=3)),
    ("noventa minutos", timedelta(minutes=90)),
    ("media hora", timedelta(minutes=30)),
    ("un cuarto de hora", timedelta(minutes=15)),
    ("tres cuartos de hora", timedelta(minutes=45)),
    ("una hora y media", timedelta(hours=1, minutes=30)),
    ("dos horas y media", timedelta(hours=2, minutes=30)),
    ("2 dias 4 horas", timedelta(days=2, hours=4)),
    ("1 hora 30 minutos", timedelta(hours=1, minutes=30)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ["2 meses", "hola mundo"])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None
