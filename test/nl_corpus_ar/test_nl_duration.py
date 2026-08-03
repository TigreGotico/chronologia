# -*- coding: utf-8 -*-
"""Durations in ar: extract_duration -> timedelta."""
from datetime import timedelta

import pytest

from chronologia.extract import extract_duration

LANG = "ar"

_CASES = [
    ('5 دقائق', timedelta(minutes=5)),
    ('45 دقائق', timedelta(minutes=45)),
    ('2 ساعة', timedelta(hours=2)),
    ('1 ساعة', timedelta(hours=1)),
    ('2 يوم', timedelta(days=2)),
    ('3 أسبوع', timedelta(weeks=3)),
    ('90 دقائق', timedelta(minutes=90)),
    ('نصف ساعة', timedelta(minutes=30)),
    ('ربع ساعة', timedelta(minutes=15)),
    ('2 يوم 4 ساعة', timedelta(days=2, hours=4)),
    ('1 ساعة 30 دقائق', timedelta(hours=1, minutes=30)),
    # dual-noun "two hours/days/weeks" fused into a single word (2 x unit)
    ('ساعتان و30 دقيقة', timedelta(hours=2, minutes=30)),
    ('ساعتين و30 دقيقة', timedelta(hours=2, minutes=30)),
    ('ساعتان', timedelta(hours=2)),
    ('يومين', timedelta(days=2)),
    ('أسبوعين', timedelta(weeks=2)),
]


@pytest.mark.parametrize("text,expected", _CASES)
def test_duration(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


@pytest.mark.parametrize("text", ['2 يونيو', 'لا شيء زمني هنا'])
def test_not_a_duration(text):
    assert extract_duration(text, LANG) is None


# Arabic writes the "and" conjunction glued onto the next word ("خمسة وعشرون"),
# so a spelled compound 21-99 (and hundred+tens) used to stall after its first
# word and return None.  The glued cardinal surfaces now fold correctly.
_WAW_CASES = [
    ('خمسة وعشرين يوما', timedelta(days=25)),
    ('واحد وعشرين يوما', timedelta(days=21)),
    ('ثلاثة وثلاثين يوما', timedelta(days=33)),
    ('مئة وخمسة وعشرين يوما', timedelta(days=125)),
]


@pytest.mark.parametrize("text,expected", _WAW_CASES)
def test_duration_waw_glued_compound(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None, f"{text!r} did not parse as a duration"
    assert got[0] == expected


# The waw conjunction fuses onto the fraction word (ونصف = و+نصف), so the
# trailing "... and a half/quarter" idiom must attach off the fused token.
@pytest.mark.parametrize("text,expected", [
    ('ساعتان ونصف', timedelta(hours=2, minutes=30)),
    ('ساعتان وربع', timedelta(hours=2, minutes=15)),
    ('1 ساعة ونصف', timedelta(hours=1, minutes=30)),
])
def test_duration_waw_fused_fraction(text, expected):
    got = extract_duration(text, LANG)
    assert got is not None and got[0] == expected
