# -*- coding: utf-8 -*-
"""Confusables corpus for et -- temporal-looking tokens that must NOT bind.

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
    'sekund kannatust',
    'oota sekund',
    'teisel korrusel',
    'väike detail',
    'vannitoas',
    'kord elus',
    'poole nii halb',
    'pool tõde',
    'pool kilo leiba',
    'veerand elanikkonnast',
    'miljon põhjust',
    'tuhandeid inimesi',
    'tõusev päike',
    'vara hommikul',
    'sekund vaikust',
    'enamik inimesi',
    'paar päeva',
    'peotäis inimesi',
    'esimesel korrusel',
    'aeg süüa',
    'pööre poole võrra',
    'keskpäeva paiku',
    'poole meeskonnast',
    'väike kogus',
    'eelmisel kuul',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_RESOLVED = [
    'kaotatud aastakümme',
]

_LIMITATIONS = [
    pytest.param(
        'aprill kui nimi',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'juuni kui nimi',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'rahvaste kevad',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'elu sügis',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'jõulud tulid vara',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('väike detail 3 päeva pärast', 'detail'),
    ('miljon põhjust 2 nädala pärast', 'miljon'),
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