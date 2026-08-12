"""R135 (German): the adjacent duration marker "für" is consumed from the
``recur_for`` vocabulary, same as English "for" -- see the English
``test_nl_r135_duration_marker.py`` for the full defect writeup.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "de"


def test_bare_fuer_duration_marker_consumed():
    d, rem = extract_duration("für 90 Minuten", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""


def test_leading_words_before_fuer_marker_consumed():
    d, rem = extract_duration("warten für 90 Minuten", LANG)
    assert d == timedelta(minutes=90)
    assert rem == "warten"


def test_bare_duration_unchanged():
    d, rem = extract_duration("90 Minuten", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""
