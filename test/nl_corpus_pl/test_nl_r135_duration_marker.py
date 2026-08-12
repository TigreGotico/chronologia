"""R135 (Polish): the adjacent duration marker "przez" is consumed from the
``recur_for`` vocabulary, same as English "for" -- see the English
``test_nl_r135_duration_marker.py`` for the full defect writeup.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "pl"


def test_bare_przez_duration_marker_consumed():
    d, rem = extract_duration("przez 90 minut", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""


def test_leading_words_before_przez_marker_consumed():
    d, rem = extract_duration("czekać przez 90 minut", LANG)
    assert d == timedelta(minutes=90)
    assert rem == "czekać"


def test_bare_duration_unchanged():
    d, rem = extract_duration("90 minut", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""
