# -*- coding: utf-8 -*-
"""Recurrence in Spanish: ``extract_recurrence(text, "es")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    ("cada viernes", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("cada lunes", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("cada dia", "FREQ=DAILY", ""),
    ("cada mes", "FREQ=MONTHLY", ""),
    ("cada año", "FREQ=YEARLY", ""),
    ("cada dos semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("mensualmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    ("el segundo martes de cada mes", "FREQ=MONTHLY;BYDAY=2TU", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["viernes", "el lunes"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
