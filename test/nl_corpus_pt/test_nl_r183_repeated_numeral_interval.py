# -*- coding: utf-8 -*-
"""pt "de N em N <unit>" -- the repeated-numeral interval idiom.

The pattern restates the same count between "de" (from) and "em" (in)
instead of a single "cada N" quantifier: "de quinze em quinze dias" is the
ordinary European Portuguese way to say "every 15 days". The repeated
numeral IS the interval; the two counts must agree or the phrase names no
coherent recurrence.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"

_CASES = [
    # masc "quinze"/"quinze" -- the number word itself has no gender to
    # disagree on.
    ("de quinze em quinze dias", "FREQ=DAILY;INTERVAL=15", ""),
    # masc "dois"/"dois".
    ("de dois em dois dias", "FREQ=DAILY;INTERVAL=2", ""),
    # fem "duas"/"duas" (weeks are feminine in pt) -- gender agreement on the
    # numeral must not matter: both fold to the plain value 2.
    ("de duas em duas semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("de três em três meses", "FREQ=MONTHLY;INTERVAL=3", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_repeated_numeral_interval(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_mismatched_numerals_decline():
    """"de dois em três dias" names no coherent interval -- the two counts
    disagree, so the phrase must refuse rather than guess either one."""
    assert extract_recurrence("de dois em três dias", LANG) is None


# The existing "a cada N <unit>" quantifier reading is untouched by this
# idiom's addition -- both readings reach the same RRULE.
def test_cada_quantifier_control_unchanged():
    got = extract_recurrence("a cada quinze dias", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY;INTERVAL=15"
