# -*- coding: utf-8 -*-
"""(da): the fused "halvanden <unit>" idiom (== "one and one half",
standard Danish for 1.5) must resolve, not misread as 0.5.

numtag reads "halvanden" as the fraction 1.5, not as 0.5.  See docs/languages/da.md.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "da"


def test_fused_halvanden_hour_idiom():
    got = extract_duration("halvanden time", LANG)
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
    got = extract_duration("mødet varer halvanden time i dag", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "mødet" in got.remainder
    assert "dag" in got.remainder


@pytest.mark.parametrize("text", ["2 juni", "ingenting tidsmæssigt her"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None