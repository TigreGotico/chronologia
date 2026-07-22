# -*- coding: utf-8 -*-
"""Confusables corpus for hu -- temporal-looking tokens that must NOT bind.

Each case is a natural sentence carrying a token that *looks* temporal but
is not meant that way (a month homograph used as a name or common word, a
unit or number word with no count, a weekday homograph, a season word in a
metaphor, an era initial, a scale word). The desired outcome is one of two:

  * ``extract_timespan`` returns ``None`` -- nothing temporal to bind; or
  * it binds a genuinely temporal part of the sentence and the confusable
    token lands in the remainder (the span-elsewhere cases).

Structurally-safe classes (unit-without-a-number, number words, era
initials, scale words) are asserted as hard ``None``. The residue -- bare
month/weekday content-word homographs, morning/tomorrow, figurative season
and unit uses, idioms -- are *documented limitations*: the parser binds the
token, disambiguation is a downstream (NLU/consumer) concern. They are
marked ``xfail`` (non-strict) so the file records the honest behaviour and
flips to green the day a guard or a downstream policy resolves them. See the
"Known limitations" section of docs/extraction.md.
"""
import pytest

from ._corpus import parse, nomatch  # noqa: F401


_SAFE_NONE = [
    'várj egy másodpercet',
    'egy másodperc türelem',
    'a második emeleten',
    'apró részlet',
    'a fürdőszobában',
    'egyszer az életben',
    'fele olyan rossz',
    'az igazság fele',
    'fél kiló kenyér',
    'a népesség negyede',
    'egymillió ok',
    'emberek ezrei',
    'felkelő nap',
    'kora reggel',
    'egy másodperc csend',
    'a legtöbb ember',
    'néhány nap',
    'egy maroknyi ember',
    'az első emeleten',
    'ideje enni',
    'fél fordulat',
    'a csapat fele',
    'apró mennyiség',
    'egy szelet kenyér',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'április mint név',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'a népek tavasza',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'az élet ősze',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'egy elveszett évtized',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=False)),
    pytest.param(
        'hét mint szám',
        marks=pytest.mark.xfail(reason='bare month homograph used as a common word binds as the month; homograph disambiguation is a downstream (NLU) concern', strict=False)),
    pytest.param(
        'hét nap múlva',
        marks=pytest.mark.xfail(reason='bare month homograph used as a common word binds as the month; homograph disambiguation is a downstream (NLU) concern', strict=False)),
    pytest.param(
        'korán jött a karácsony',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=False)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('apró részlet 3 nap múlva', 'részlet'),
    ('egymillió ok 2 hét múlva', 'millió'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
