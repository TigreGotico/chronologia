# -*- coding: utf-8 -*-
"""Recurrence in Portuguese: ``extract_recurrence(text, "pt")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"

_CASES = [
    ("cada sexta-feira", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("cada segunda-feira", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("cada dia", "FREQ=DAILY", ""),
    ("cada mês", "FREQ=MONTHLY", ""),
    ("cada ano", "FREQ=YEARLY", ""),
    ("cada duas semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("semanalmente", "FREQ=WEEKLY", ""),
    ("mensalmente", "FREQ=MONTHLY", ""),
    ("anualmente", "FREQ=YEARLY", ""),
    ("diariamente", "FREQ=DAILY", ""),
    ("a primeira segunda-feira de cada mês", "FREQ=MONTHLY;BYDAY=1MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["sexta-feira", "a segunda-feira"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
