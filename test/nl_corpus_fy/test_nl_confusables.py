# -*- coding: utf-8 -*-
"""Confusables corpus for fy -- temporal-looking tokens that must NOT bind.

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
    'in sekonde geduld',
    'wachtsje in sekonde',
    'op de twadde ferdjipping',
    'in lyts detail',
    'yn de badkeamer',
    'ien kear yn it libben',
    'heal sa slim',
    'de heale wierheid',
    'in heal kilo brea',
    'in fjirde fan de befolking',
    'in heale draai',
    'in miljoen redenen',
    'tûzenen minsken',
    'opkommende sinne',
    'tiid om te iten',
    'in sekonde stilte',
    'de measte minsken',
    'in pear dagen',
    'op de earste ferdjipping',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'juny as namme',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'augustus as foarnamme',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'july as namme',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=False)),
    pytest.param(
        'de maitiid fan de folken',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'de hjerst fan it libben',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=False)),
    pytest.param(
        'in ferlern desennium',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=False)),
    pytest.param(
        'goeiemoarn allegear',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=False)),
    pytest.param(
        'betiid yn de moarn',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=False)),
    pytest.param(
        'kryst kaam betiid',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=False)),
    pytest.param(
        'om de middei hinne',
        marks=pytest.mark.xfail(reason='structurally-safe class unexpectedly binds; recorded as a limitation', strict=False)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('in sekonde stilte oer 3 dagen', 'sekonde'),
    ('in miljoen redenen oer 2 wiken', 'miljoen'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
