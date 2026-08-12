# -*- coding: utf-8 -*-
"""R133 (sv): the "one and one half <unit>" idiom must resolve to 1.5x the
unit, not silently truncate to the trailing "en halv <unit>" (0.5x) reading
with the leading "en och" stranded in the remainder.

"en och en halv timme" == "one and one half hour(s)" == 90 minutes.  Before
the fix this returned 30 minutes with "en och" left over -- a silent WRONG
answer, not a refusal.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "sv"


def test_one_and_a_half_hour_idiom():
    got = extract_duration("en och en halv timme", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_one_and_a_half_day_idiom():
    got = extract_duration("en och en halv dag", LANG)
    assert got is not None
    assert got.duration == timedelta(days=1, hours=12)
    assert got.remainder.strip() == ""


def test_fused_halvannan_idiom():
    # "halvannan timme" -- the older, still-valid fused form of "1.5 hours".
    got = extract_duration("halvannan timme", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    # The plain "half an hour" idiom must still read as 30 minutes, not be
    # dragged up to 90 minutes by the new "and one half" handling.
    got = extract_duration("en halv timme", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 timmar", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("mötet varar en och en halv timme idag", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "mötet" in got.remainder
    assert "idag" in got.remainder


@pytest.mark.parametrize("text", ["2 juni", "inget tidsligt här"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
