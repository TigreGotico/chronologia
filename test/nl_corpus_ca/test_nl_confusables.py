# -*- coding: utf-8 -*-
"""Confusables corpus for ca -- temporal-looking tokens that must NOT bind.

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
    'un segon si us plau',
    'el segon pis',
    'detall minúscul',
    'quarto de bany',
    'hora de dinar',
    'una vegada a la vida',
    'mitja veritat',
    'un quart de la població',
    'fer mitja volta',
    'un milió de raons',
    'milers de persones',
    'sol naixent',
    'la meitat del pastís',
    'mig quilo de pa',
    'un parell de dies',
    'la majoria de la gent',
    'un segon de silenci',
    'el segon plat',
    'mitja hora',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_RESOLVED = [
    'al matí ben aviat',
]

_LIMITATIONS = [
    pytest.param(
        'abril nom de nena',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'maig nom de gos',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'la primavera dels pobles',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'la tardor de la vida',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'una dècada perduda',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=True)),
    pytest.param(
        'diumenge canta òpera',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'dimarts nom propi',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'dissabte de glòria',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'el nadal va arribar aviat',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('un milió de raons dintre de 2 setmanes', 'milió'),
    ('milers de persones dintre de 3 dies', 'milers'),
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