# -*- coding: utf-8 -*-
"""R147 (fr) -- "N jours apres/avant demain/hier" dropped its numeral,
mirroring the English/German defect, PLUS a French-specific wrinkle: the
fused idiom vocabulary ("apres demain"/"avant hier", the space-spelled
sibling of the hyphenated "apres-demain"/"avant-hier") folds the two words
into ONE token before the matcher ever runs (``numfold_romance._FR_PHRASES``
via ``_collapse_phrase``, re-applied by the generic multiword-vocab merge in
``pipeline.merge_multiword``), so "apres"/"avant" was never even available
as a separate directional-marker token for the numeral-scaled offset to
bind -- worse than the bare idiom-vs-offset overlap collision en/de have.

FIX: both fusion sites (``numfold_romance._collapse_phrase`` and
``pipeline.merge_multiword``) hold back collapsing "apres demain"/"avant
hier" specifically when a ``[NUM] UNIT`` pre-amble ("deux jours") heads
them -- in that shape "apres"/"avant" is the offset's directional MARKER,
not part of the fixed idiom. A bare, unpre-ambled "apres-demain"/"apres
demain"/"avant-hier"/"avant hier" still fuses and resolves to the fixed
+/-2-day idiom exactly as before.

Expected values are independently hand-computed against the anchor (plain
calendar-day arithmetic), never read back from the parser.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_timespan

LANG = "fr"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday
_TOMORROW = datetime(2026, 8, 14, 0, 0)
_YESTERDAY = datetime(2026, 8, 12, 0, 0)


def _span(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end, r.remainder


# -- the defect: numeral must multiply the day-idiom offset -----------------

@pytest.mark.parametrize("n_word,n", [("deux", 2), ("2", 2),
                                       ("trois", 3), ("3", 3)])
def test_num_jours_apres_demain(n_word, n):
    expected = _TOMORROW + timedelta(days=n)
    start, end, remainder = _span(f"{n_word} jours apres demain")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("deux", 2), ("2", 2),
                                       ("trois", 3), ("3", 3)])
def test_num_jours_avant_demain(n_word, n):
    expected = _TOMORROW - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} jours avant demain")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("deux", 2), ("2", 2),
                                       ("trois", 3), ("3", 3)])
def test_num_jours_apres_hier(n_word, n):
    expected = _YESTERDAY + timedelta(days=n)
    start, end, remainder = _span(f"{n_word} jours apres hier")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("deux", 2), ("2", 2),
                                       ("trois", 3), ("3", 3)])
def test_num_jours_avant_hier_numeral(n_word, n):
    # NB: "avant hier" (no leading numeral) is ITSELF a fused idiom
    # ("the day before yesterday", anchor-2). Prefixed with a numeral it
    # unambiguously reads as the offset instead: yesterday - N.
    expected = _YESTERDAY - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} jours avant hier")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


# -- fused idiom controls: must NOT change -----------------------------------

def test_control_apres_demain_hyphenated_unchanged():
    start, end, remainder = _span("après-demain")
    assert start == datetime(2026, 8, 15, 0, 0)
    assert end == datetime(2026, 8, 16, 0, 0)
    assert remainder == ""


def test_control_apres_demain_space_unchanged():
    start, end, remainder = _span("apres demain")
    assert start == datetime(2026, 8, 15, 0, 0)
    assert end == datetime(2026, 8, 16, 0, 0)
    assert remainder == ""


def test_control_avant_hier_hyphenated_unchanged():
    start, end, remainder = _span("avant-hier")
    assert start == datetime(2026, 8, 11, 0, 0)
    assert end == datetime(2026, 8, 12, 0, 0)
    assert remainder == ""


def test_control_avant_hier_space_unchanged():
    start, end, remainder = _span("avant hier")
    assert start == datetime(2026, 8, 11, 0, 0)
    assert end == datetime(2026, 8, 12, 0, 0)
    assert remainder == ""
