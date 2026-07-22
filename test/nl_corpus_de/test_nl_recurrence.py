# -*- coding: utf-8 -*-
"""Recurrence in German: ``extract_recurrence(text, "de")`` -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "de"

_CASES = [
    ("jeden freitag", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("jeden montag", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("jeden tag", "FREQ=DAILY", ""),
    ("jeden monat", "FREQ=MONTHLY", ""),
    ("jedes jahr", "FREQ=YEARLY", ""),
    ("alle zwei wochen", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("wöchentlich", "FREQ=WEEKLY", ""),
    ("monatlich", "FREQ=MONTHLY", ""),
    ("jährlich", "FREQ=YEARLY", ""),
    ("täglich", "FREQ=DAILY", ""),
    ("jeden wochentag", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", ""),
    ("jeden ersten montag im monat", "FREQ=MONTHLY;BYDAY=1MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ["freitag", "nächste woche"])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None
