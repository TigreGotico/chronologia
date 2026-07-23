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
marked ``xfail(strict=True)`` so the file records the honest behaviour and
fails loudly (an XPASS) the day a guard or a downstream policy resolves
them -- forcing the case to be promoted to a real assertion rather than
silently starting to pass. See the
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


_RESOLVED = [
    'a népek tavasza',
    'az élet ősze',
    'egy elveszett évtized',
    'hét mint szám',
]

_LIMITATIONS = [
    pytest.param(
        'április mint név',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'hét nap múlva',
        marks=pytest.mark.xfail(reason='bare month homograph used as a common word binds as the month; homograph disambiguation is a downstream (NLU) concern', strict=True)),
    pytest.param(
        'korán jött a karácsony',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
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



@pytest.mark.parametrize("text", _RESOLVED)
def test_confusable_now_none(text):
    # formerly a documented limitation; the parser now correctly
    # binds nothing here.  A strict tripwire would misfire, so this is
    # a live positive assertion of the now-correct behaviour.
    nomatch(text)