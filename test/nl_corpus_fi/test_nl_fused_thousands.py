# -*- coding: utf-8 -*-
"""Finnish fused round-thousand durations: the multiplier is glued to the
partitive scale word in one token ("kaksituhatta" = kaksi + tuhatta = 2000,
"kolmetuhatta" = 3000), with the sub-thousand chunk spaced ("kaksituhatta neljä"
= 2004).

Before the fold learned the fused spelling the leading thousands component was
silently dropped: "kaksituhatta neljä päivää" folded to 4 days and the bare
"kaksituhatta päivää" returned None.  Gold is independent arithmetic.
"""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "fi"

_CASES = [
    ('kaksituhatta neljä päivää', timedelta(days=2004)),   # was 4
    ('kaksituhatta päivää', timedelta(days=2000)),         # was None
    ('kolmetuhatta viisi päivää', timedelta(days=3005)),   # was 5
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_fused_thousands(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text,expected", [
    ('satakaksikymmentäkolme päivää', timedelta(days=123)),
])
def test_sub_thousand_regression_guard(text, expected):
    # The plain spelled sub-thousand fold must keep working after the fused
    # round-thousand pre-pass is inserted ahead of it.
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
