# -*- coding: utf-8 -*-
"""R133 (sk): "hodinu a pol" -- a bare unit with NO leading count, followed
by the trailing "a pol" (and-a-half) idiom -- must resolve to 90 minutes,
the implicit leading count of one ("an hour") being unwritten as in cs.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "sk"


def test_bare_unit_and_half_idiom():
    got = extract_duration("hodinu a pol", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("pol hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("stretnutie trvá hodinu a pol dnes", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "stretnutie" in got.remainder
    assert "dnes" in got.remainder


@pytest.mark.parametrize("text", ["2. júna", "nič časové tu"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
