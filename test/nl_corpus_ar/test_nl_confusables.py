# -*- coding: utf-8 -*-
"""Confusables corpus for ar -- temporal-looking tokens that must NOT bind.

Each case is a natural sentence carrying a token that *looks* temporal but is
not meant that way (a month homograph used as a verb or name, a season word
in a metaphor, a unit or number word with no count, a scale word, a bare
weekday). The desired outcome is one of two:

  * ``extract_timespan`` returns ``None`` -- nothing temporal to bind; or
  * it binds a genuinely temporal part of the sentence and the confusable
    token lands in the remainder (the span-elsewhere cases).

Structurally-safe classes (unit/number/scale word with no count, bare
weekday -- which needs a relative marker to form a construction) are asserted
as hard ``None``. The residue -- bare month/season content-word homographs
(مارس "he practiced" == March, ربيع a name == spring) -- are *documented
limitations*: the parser binds the token, disambiguation is a downstream
concern. They are marked ``xfail(strict=True)``. See the "Known limitations"
section of docs/extraction.md.
"""
import pytest

from ._corpus import parse, nomatch  # noqa: F401


_SAFE_NONE = [
    'ثلاثة كتب على الطاولة',      # "three books" -- number, no unit
    'خمسة أشخاص',                # "five people" -- number, no unit
    'عشرة أصابع',                # "ten fingers"
    'اشتريت ساعة جديدة',          # "I bought a new watch" -- hour word, no count
    'دقيقة من فضلك',             # "a minute please" -- unit, no count
    'أحد الأشخاص',               # "one of the people" -- Sunday homograph, bare
    'بعد ذلك',                   # "after that" -- lone direction marker
    'قبل كل شيء',                # "before everything" -- lone past marker
    'منذ زمن طويل',              # "since a long time" -- marker, no count
    'نصف الكمية',                # "half the amount"
    'مليون سبب',                 # "a million reasons" -- scale word, no year
    'الرأي العام',               # "public opinion" -- عام (public) vs عام (year)
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'مارس الرياضة',
        marks=pytest.mark.xfail(reason='month homograph مارس ("he practiced") binds as March; disambiguation is downstream', strict=True)),
    pytest.param(
        'ربيع اسم جميل',
        marks=pytest.mark.xfail(reason='season word ربيع used as a person name binds as spring; downstream concern', strict=True)),
    pytest.param(
        'الصيف الحار',
        marks=pytest.mark.xfail(reason='season word in a descriptive phrase binds as the season; downstream concern', strict=True)),
    pytest.param(
        'السبت المقدس',
        marks=pytest.mark.xfail(reason='full weekday السبت ("Saturday") binds as the next Saturday inside the proper name "Holy Saturday"; the bare-weekday order resolves the day, disambiguation is downstream', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('مليون سبب بعد 3 أيام', 'مليون'),
    ('ثلاثة كتب قبل 5 سنوات', 'كتب'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
