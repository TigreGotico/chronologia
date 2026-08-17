# -*- coding: utf-8 -*-
"""fr "de N en N <unit>" -- the repeated-numeral interval idiom.

French restates the same count between "de" (from) and "en" (in) instead of
a single "tous les N" quantifier: "de deux en deux jours" is the ordinary
way to say "every 2 days". The repeated numeral IS the interval; the two
counts must agree or the phrase names no coherent recurrence.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "fr"

_CASES = [
    ("de deux en deux jours", "FREQ=DAILY;INTERVAL=2", ""),
    ("de quinze en quinze jours", "FREQ=DAILY;INTERVAL=15", ""),
    ("de trois en trois mois", "FREQ=MONTHLY;INTERVAL=3", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_repeated_numeral_interval(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_mismatched_numerals_decline():
    """"de deux en trois jours" names no coherent interval -- the two counts
    disagree, so the phrase must refuse rather than guess either one."""
    assert extract_recurrence("de deux en trois jours", LANG) is None


# The existing "tous les N <unit>" quantifier reading is untouched by this
# idiom's addition -- both readings reach the same RRULE.
def test_tous_les_quantifier_control_unchanged():
    got = extract_recurrence("tous les deux jours", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY;INTERVAL=2"
