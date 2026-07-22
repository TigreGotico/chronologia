# -*- coding: utf-8 -*-
"""Recurrence in French: ``extract_recurrence(text, "fr")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fr"

_CASES = [
    ("chaque vendredi", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("chaque lundi", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("chaque samedi", "FREQ=WEEKLY;BYDAY=SA", ""),
    ("chaque jour", "FREQ=DAILY", ""),
    ("chaque mois", "FREQ=MONTHLY", ""),
    ("chaque année", "FREQ=YEARLY", ""),
    ("toutes les deux semaines", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("tous les jours", "FREQ=DAILY", ""),
    ("mensuellement", "FREQ=MONTHLY", ""),
    ("annuellement", "FREQ=YEARLY", ""),
    ("quotidiennement", "FREQ=DAILY", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["vendredi", "le lundi"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
