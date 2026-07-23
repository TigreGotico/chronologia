# -*- coding: utf-8 -*-
"""Folded spelled-number tokens must preserve their character extent.

When a maximal run of number-words is folded to a single synthesised digit
token, that token must carry ``char_start``/``char_end`` covering the run --
exactly as the Latin (en/romance/germanic) fold in ``numfold.py`` does.  When
the folded token sits at a mention edge, ``char_span`` degrades to ``None``
without the offsets, and ``utterance[char_span[0]:char_span[1]]`` can no longer
recover the surface.

Regression guard for the semitic / slavic / agglutinative fold families, which
previously synthesised the digit token with the default ``None`` offsets.
"""
import pytest

from chronologia.extract import extract_timespans


# Each phrase places the spelled number at the LEFT edge of the (single)
# mention, so the folded token is the char_span's start token.  The mention
# surface is the whole phrase; recovering it from char_span must round-trip.
_LEFT_EDGE = [
    # slavic
    ("ru", "три дня назад"),
    ("uk", "три дні тому"),
    ("pl", "trzy dni temu"),
    # semitic (spelled day number opening a date)
    ("ar", "خمسة يناير"),
    ("he", "חמישה בינואר"),
    # agglutinative
    ("hu", "három nappal ezelőtt"),
    ("fi", "kolme päivää sitten"),
    ("et", "kolm päeva tagasi"),
]


@pytest.mark.parametrize("lang,text", _LEFT_EDGE)
def test_left_edge_spelled_number_preserves_char_span(lang, text):
    ms = extract_timespans(text, lang)
    assert ms, f"{lang}: expected a mention for {text!r}"
    m = ms[0]
    assert m.char_span is not None, f"{lang}: char_span degraded to None for {text!r}"
    cs, ce = m.char_span
    assert text[cs:ce] == text, (
        f"{lang}: char_span {(cs, ce)} does not recover surface for {text!r}; "
        f"got {text[cs:ce]!r}"
    )


# Non-None guard across the affected locales (prepositional openers already
# worked; spelled-at-edge ones did not).  All must recover a substring.
_BATTERY = [
    ("ru", "три дня назад"),
    ("uk", "три дні тому"),
    ("pl", "trzy dni temu"),
    ("hr", "prije tri dana"),
    ("bg", "преди три дни"),
    ("el", "πριν τρεις ημέρες"),
    ("ar", "خمسة يناير"),
    ("he", "חמישה בינואר"),
    ("hu", "három nappal ezelőtt"),
    ("fi", "kolme päivää sitten"),
    ("et", "kolm päeva tagasi"),
    ("eu", "duela hiru egun"),
]


@pytest.mark.parametrize("lang,text", _BATTERY)
def test_battery_char_span_recovers_substring(lang, text):
    ms = extract_timespans(text, lang)
    assert ms, f"{lang}: expected a mention for {text!r}"
    m = ms[0]
    assert m.char_span is not None, f"{lang}: char_span is None for {text!r}"
    cs, ce = m.char_span
    assert 0 <= cs < ce <= len(text)
    assert text[cs:ce] in text
