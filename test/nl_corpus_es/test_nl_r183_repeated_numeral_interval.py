# -*- coding: utf-8 -*-
"""es "de N en N <unit>" -- the repeated-numeral interval idiom.

Spanish restates the same count between "de" (from) and "en" (in) instead of
a single "cada N" quantifier: "de quince en quince días" is the ordinary way
to say "every 15 days". The repeated numeral IS the interval; the two counts
must agree or the phrase names no coherent recurrence.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "es"

_CASES = [
    ("de quince en quince días", "FREQ=DAILY;INTERVAL=15", ""),
    ("de dos en dos días", "FREQ=DAILY;INTERVAL=2", ""),
    ("de dos en dos semanas", "FREQ=WEEKLY;INTERVAL=2", ""),
    ("de tres en tres meses", "FREQ=MONTHLY;INTERVAL=3", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_repeated_numeral_interval(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_mismatched_numerals_decline():
    """"de dos en tres días" names no coherent interval -- the two counts
    disagree, so the phrase must refuse rather than guess either one."""
    assert extract_recurrence("de dos en tres días", LANG) is None


# The existing "cada N <unit>" quantifier reading is untouched by this
# idiom's addition -- both readings reach the same RRULE.
def test_cada_quantifier_control_unchanged():
    got = extract_recurrence("cada quince días", LANG)
    assert got is not None
    assert got[0].to_string() == "FREQ=DAILY;INTERVAL=15"
