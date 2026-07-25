"""English contract for the vernacular Roman within-month anchors (Kalends,
Nones, Ides) and their composition with ordinary offset arithmetic.

The everyday "the ides of march" surface is unambiguous and on by default
(unlike the raw-Latin ``ante diem`` a.d.-count formula, which stays gated
behind ``enable=('classical',)`` -- see ``test_nl_historical.py``). This file
locks the English showcase: any offset x any named anchor composes for free
through the anchored-arithmetic engine.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _start(text, **kwargs):
    r = extract_timespan(text, "en", ANCHOR, **kwargs)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start_datetime


# -- classical (raw-Latin) a.d.-count formula: opt-in only ----------------

@pytest.mark.parametrize("text,iso,enable", [
    ("ante diem III kalendas apriles", (2017, 3, 30), ("classical",)),
    ("ante diem IV idus martias", (2017, 3, 12), ("classical",)),
])
def test_classical_formula_enabled(text, iso, enable):
    got = _start(text, enable=enable)
    assert (got.year, got.month, got.day) == iso


def test_classical_formula_off_by_default():
    assert extract_timespan("ante diem III kalendas apriles", "en", ANCHOR) is None


# -- English vernacular Kalends/Nones/Ides x offset composition -----------

@pytest.mark.parametrize("text,iso", [
    ("a week before the ides of march", (2017, 3, 8)),
    ("3 days after the kalends of april", (2017, 4, 4)),
    ("the day before the nones of july", (2017, 7, 6)),
])
def test_vernacular_offset_composition(text, iso):
    got = _start(text)
    assert (got.year, got.month, got.day) == iso
