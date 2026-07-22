# -*- coding: utf-8 -*-
"""Confusables corpus for sl -- temporal-looking tokens that must NOT bind.

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
    'sekundo potrpljenja',
    'počakaj sekundo',
    'v drugem nadstropju',
    'majhna podrobnost',
    'v kopalnici',
    'enkrat v življenju',
    'napol tako slabo',
    'polovica resnice',
    'pol kile kruha',
    'četrtina prebivalstva',
    'milijon razlogov',
    'tisoče ljudi',
    'vzhajajoče sonce',
    'zgodaj zjutraj',
    'sekunda tišine',
    'večina ljudi',
    'nekaj dni',
    'peščica ljudi',
    'v prvem nadstropju',
    'čas za jesti',
    'obrat za pol',
    'okoli poldneva',
    'polovica ekipe',
    'drobna podrobnost',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'april kot ime',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'avgust kot ime',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'junij kot ime',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'pomlad narodov',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'jesen življenja',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'izgubljeno desetletje',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=False)),
    pytest.param(
        'okolje okoli nas',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=False)),
    pytest.param(
        'božič je prišel zgodaj',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=False)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('majhna podrobnost čez 3 dni', 'podrobnost'),
    ('milijon razlogov čez 2 tedna', 'milijon'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
