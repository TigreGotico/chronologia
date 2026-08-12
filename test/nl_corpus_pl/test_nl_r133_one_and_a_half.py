# -*- coding: utf-8 -*-
"""R133 (pl): the fused "półtorej <unit>" idiom (standard Polish for 1.5,
feminine agreement with "godziny") must resolve, not refuse with None.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "pl"


def test_fused_poltorej_hour_idiom():
    got = extract_duration("półtorej godziny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("pół godziny", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 godziny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("spotkanie trwa półtorej godziny dzisiaj", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "spotkanie" in got.remainder
    assert "dzisiaj" in got.remainder


@pytest.mark.parametrize("text", ["2 czerwca", "nic czasowego tutaj"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
