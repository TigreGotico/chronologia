# -*- coding: utf-8 -*-
"""R133 (cs): two "one and a half hour" idioms must resolve to 90 minutes:

* "hodinu a půl" -- a bare unit with NO leading count, followed by the
  trailing "a půl" (and-a-half) idiom; the implicit leading count of one
  ("an hour") is not written out the way English/Swedish fold their
  indefinite article onto the count.
* "půldruhé hodiny" -- the older fused numeral (literally "half of the
  second" == 1.5) still used for "an hour and a half" in Czech.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "cs"


def test_bare_unit_and_half_idiom():
    got = extract_duration("hodinu a půl", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_fused_puldruhe_idiom():
    got = extract_duration("půldruhé hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert got.remainder.strip() == ""


def test_plain_half_hour_control_unaffected():
    got = extract_duration("půl hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(minutes=30)
    assert got.remainder.strip() == ""


def test_plain_n_unit_control_unaffected():
    got = extract_duration("2 hodiny", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=2)
    assert got.remainder.strip() == ""


def test_idiom_embedded_in_sentence():
    got = extract_duration("schůzka trvá hodinu a půl dnes", LANG)
    assert got is not None
    assert got.duration == timedelta(hours=1, minutes=30)
    assert "schůzka" in got.remainder
    assert "dnes" in got.remainder


@pytest.mark.parametrize("text", ["2. června", "nic časového tady"])
def test_not_a_duration_control(text):
    assert extract_duration(text, LANG) is None
