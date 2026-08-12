# -*- coding: utf-8 -*-
"""R133 (nb): the fused "halvannen <unit>" idiom (== "one and one half",
standard Norwegian Bokmål for 1.5) must resolve, not refuse with None.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "nb"


def test_fused_halvannen_hour_idiom():
    got = extract_duration("halvannen time", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("en halv time", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 timer", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("møtet varer halvannen time i dag", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "møtet" in got.remainder
    assert "dag" in got.remainder


@pytest.mark.parametrize("text", ["2 juni", "ingenting tidsmessig her"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
