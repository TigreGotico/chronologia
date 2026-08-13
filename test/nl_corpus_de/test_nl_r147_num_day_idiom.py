# -*- coding: utf-8 -*-
"""R147 (de) -- "N Tage nach/vor morgen/gestern" dropped its numeral, the
same defect en/fr have: the ``named_day_after``/``named_day_before`` idiom
("der Tag nach morgen", "der Tag vor gestern") has no ``NUM`` slot and still
wins the matcher's longest-span overlap contest against the generic
NUM-aware offset construction, stranding the numeral and always shifting by
a fixed 1 day.

FIX: ``timespan._num_preamble_named_day_idiom_veto`` vetoes the idiom match
whenever a NUM token immediately precedes its ``DAYUNIT`` slot, so the bare
``named_day`` match wins instead and the generic anchored-offset pass folds
the numeral-scaled offset on correctly.

Expected values are independently hand-computed against the anchor (plain
calendar-day arithmetic), never read back from the parser.
"""
from datetime import datetime, timedelta

import pytest

from chronologia.extract import extract_timespan

LANG = "de"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday
_TOMORROW = datetime(2026, 8, 14, 0, 0)
_YESTERDAY = datetime(2026, 8, 12, 0, 0)


def _span(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end, r.remainder


# -- the defect: numeral must multiply the day-idiom offset -----------------

@pytest.mark.parametrize("n_word,n", [("zwei", 2), ("2", 2),
                                       ("drei", 3), ("3", 3)])
def test_num_tage_nach_morgen(n_word, n):
    expected = _TOMORROW + timedelta(days=n)
    start, end, remainder = _span(f"{n_word} Tage nach morgen")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("zwei", 2), ("2", 2),
                                       ("drei", 3), ("3", 3)])
def test_num_tage_vor_morgen(n_word, n):
    expected = _TOMORROW - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} Tage vor morgen")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("zwei", 2), ("2", 2),
                                       ("drei", 3), ("3", 3)])
def test_num_tage_nach_gestern(n_word, n):
    expected = _YESTERDAY + timedelta(days=n)
    start, end, remainder = _span(f"{n_word} Tage nach gestern")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("zwei", 2), ("2", 2),
                                       ("drei", 3), ("3", 3)])
def test_num_tage_vor_gestern(n_word, n):
    expected = _YESTERDAY - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} Tage vor gestern")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


# -- idiom controls: must NOT change -----------------------------------------

def test_control_der_tag_nach_morgen_unchanged():
    start, end, remainder = _span("der Tag nach morgen")
    assert start == datetime(2026, 8, 15, 0, 0)
    assert end == datetime(2026, 8, 16, 0, 0)
    assert remainder == ""


def test_control_der_tag_vor_gestern_unchanged():
    start, end, remainder = _span("der Tag vor gestern")
    assert start == datetime(2026, 8, 11, 0, 0)
    assert end == datetime(2026, 8, 12, 0, 0)
    assert remainder == ""
