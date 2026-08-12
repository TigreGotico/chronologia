# -*- coding: utf-8 -*-
"""R133 (nn): the fused "halvannan <unit>" idiom (== "one and one half",
standard Nynorsk for 1.5) must resolve, not refuse with None.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "nn"


def test_fused_halvannan_hour_idiom():
    got = extract_duration("halvannan time", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("ein halv time", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 timar", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("møtet varer halvannan time i dag", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "møtet" in got.remainder
    assert "dag" in got.remainder


@pytest.mark.parametrize("text", ["2 juni", "ingenting tidsmessig her"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
