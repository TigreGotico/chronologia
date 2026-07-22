# -*- coding: utf-8 -*-
"""Confusables corpus for de -- temporal-looking tokens that must NOT bind.

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
    'eine sekunde bitte',
    'warte eine sekunde',
    'im zweiten stock',
    'ein winziges detail',
    'im badezimmer',
    'einmal im leben',
    'halb so schlimm',
    'die halbe wahrheit',
    'ein halbes kilo brot',
    'ein viertel der bevölkerung',
    'eine halbe drehung',
    'eine million gründe',
    'tausende von menschen',
    'aufgehende sonne',
    'zeit zum essen',
    'eine sekunde der stille',
    'die meisten leute',
    'ein paar tage',
    'eine handvoll leute',
    'im ersten stock',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_RESOLVED = [
    'ein verlorenes jahrzehnt',
]

_LIMITATIONS = [
    pytest.param(
        'juni als name',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'august als vorname',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'der frühling der völker',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'der herbst des lebens',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'am morgen früh',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=True)),
    pytest.param(
        'guten morgen',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=True)),
    pytest.param(
        'früh am morgen',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=True)),
    pytest.param(
        'mai ich helfen',
        marks=pytest.mark.xfail(reason='bare month homograph used as a common word binds as the month; homograph disambiguation is a downstream (NLU) concern', strict=True)),
    pytest.param(
        'weihnachten kam früh',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('eine sekunde stille in 3 tagen', 'sekunde'),
    ('die halbe wahrheit in 2 wochen', 'wahrheit'),
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