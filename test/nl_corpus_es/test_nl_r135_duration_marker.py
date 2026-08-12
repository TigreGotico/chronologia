"""R135 (Spanish): the adjacent duration marker "durante" is consumed from
the ``recur_for`` vocabulary, same as English "for" -- see the English
``test_nl_r135_duration_marker.py`` for the full defect writeup.
"""
from datetime import timedelta

from chronologia.extract import extract_duration

LANG = "es"


def test_bare_durante_duration_marker_consumed():
    d, rem = extract_duration("durante 90 minutos", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""


def test_leading_words_before_durante_marker_consumed():
    d, rem = extract_duration("esperar durante 90 minutos", LANG)
    assert d == timedelta(minutes=90)
    assert rem == "esperar"


def test_marker_separated_by_words_not_swallowed():
    r = extract_duration("reunión durante el almuerzo en 90 minutos", LANG)
    assert r is not None
    d, rem = r
    assert d == timedelta(minutes=90)
    assert rem == "reunión durante el almuerzo en"


def test_bare_duration_unchanged():
    d, rem = extract_duration("90 minutos", LANG)
    assert d == timedelta(minutes=90)
    assert rem == ""
