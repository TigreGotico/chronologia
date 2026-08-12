# -*- coding: utf-8 -*-
"""R133 (el): the fused "μιάμιση <unit>" idiom (feminine 1.5, agreeing with
feminine "ώρα"/hour) must resolve to 90 minutes, not refuse with None.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "el"


def test_fused_miamisi_hour_idiom():
    got = extract_duration("μιάμιση ώρα", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("μισή ώρα", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 ώρες", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("η συνάντηση διαρκεί μιάμιση ώρα σήμερα", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "συνάντηση" in got.remainder
    assert "σήμερα" in got.remainder


@pytest.mark.parametrize("text", ["2 Ιουνίου", "τίποτα χρονικό εδώ"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
