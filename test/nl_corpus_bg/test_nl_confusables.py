# -*- coding: utf-8 -*-
"""Confusables corpus for bg -- temporal-looking tokens that must NOT bind.

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
    'секунда търпение',
    'изчакай секунда',
    'на втория етаж',
    'малка подробност',
    'в банята',
    'веднъж в живота',
    'наполовина толкова зле',
    'половината истина',
    'половин кило хляб',
    'четвърт от населението',
    'милион причини',
    'хиляди хора',
    'изгряващо слънце',
    'рано сутрин',
    'секунда тишина',
    'повечето хора',
    'няколко дни',
    'шепа хора',
    'на първия етаж',
    'време за ядене',
    'завой на половина',
    'около обяд',
    'половината отбор',
    'дребна подробност',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'април като име',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'август като име',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'юни като име',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'пролетта на народите',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'есента на живота',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'изгубено десетилетие',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=False)),
    pytest.param(
        'околна среда',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=False)),
    pytest.param(
        'коледа дойде рано',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=False)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('малка подробност след 3 дни', 'подробност'),
    ('милион причини след 2 седмици', 'милион'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
