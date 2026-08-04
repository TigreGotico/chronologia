# -*- coding: utf-8 -*-
"""Hungarian fused round-thousand durations: "kétezer" (2×1000) glued to the
scale word, with the sub-thousand chunk hyphenated ("kétezer-huszonnégy" = 2024,
the ordinary spelling of the year 2024) or spaced.

Before the fold learned the fused spelling the leading thousands component was
silently dropped: "kétezer-huszonnégy nap" folded to 24 days, "háromezer-öt nap"
to 5, and the bare "kétezer nap" returned None.  Gold is independent arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "hu"

_CASES = [
    ('kétezer-huszonnégy nap', timedelta(days=2024)),   # was 24
    ('kétezer huszonnégy nap', timedelta(days=2024)),   # was 24 (spaced)
    ('kétezer-tizenöt nap', timedelta(days=2015)),      # was 15
    ('háromezer-öt nap', timedelta(days=3005)),         # was 5
    ('kétezer nap', timedelta(days=2000)),              # was None
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_fused_thousands(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,expected", [
    ('százhuszonhárom nap', timedelta(days=123)),
])
def test_sub_thousand_regression_guard(text, expected):
    # The plain spelled sub-thousand fold must keep working after the fused
    # round-thousand pre-pass is inserted ahead of it.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
