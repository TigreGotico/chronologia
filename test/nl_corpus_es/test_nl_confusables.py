# -*- coding: utf-8 -*-
"""Confusables corpus for es -- temporal-looking tokens that must NOT bind.

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
    'un segundo por favor',
    'espera un segundo',
    'el segundo piso',
    'un minuto detalle',
    'el cuarto de baño',
    'detalle minúsculo',
    'una vez en la vida',
    'media verdad',
    'un cuarto de la población',
    'dar media vuelta',
    'un millón de razones',
    'miles de personas',
    'sol naciente',
    'hora de comer',
    'un segundo de silencio',
    'la mitad del pastel',
    'medio kilo de pan',
    'un par de días',
    'la mayoría de la gente',
]


@pytest.mark.parametrize("text", _SAFE_NONE)
def test_confusable_returns_none(text):
    # structurally safe: no count/modifier, nothing to bind.
    nomatch(text)


_LIMITATIONS = [
    pytest.param(
        'abril nombre de niña',
        marks=pytest.mark.xfail(reason='month homograph used as a person/pet name binds as the month; expected limitation, disambiguation is downstream', strict=True)),
    pytest.param(
        'la primavera de los pueblos',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'el otoño de la vida',
        marks=pytest.mark.xfail(reason='season word in figurative use binds as the season; downstream concern', strict=True)),
    pytest.param(
        'una década perdida',
        marks=pytest.mark.xfail(reason='temporal unit in figurative use binds as a date; downstream concern', strict=True)),
    pytest.param(
        'por la mañana temprano',
        marks=pytest.mark.xfail(reason='morning/tomorrow homograph binds as the next day; expected limitation', strict=True)),
    pytest.param(
        'domingo canta ópera',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'el señor domingo llegó',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'martes nombre propio',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'sábado gloria',
        marks=pytest.mark.xfail(reason='weekday homograph binds as the weekday once bare-weekday parsing lands engine-wide; downstream concern', strict=True)),
    pytest.param(
        'la navidad llegó temprano',
        marks=pytest.mark.xfail(reason='temporal token inside a fixed idiom binds literally; downstream concern', strict=True)),
]


@pytest.mark.parametrize("text", _LIMITATIONS)
def test_documented_limitation(text):
    # desired outcome is None; the parser binds the confusable token.
    nomatch(text)


_SPAN_ELSEWHERE = [
    ('un millón de razones dentro de 2 semanas', 'millón'),
    ('miles de personas dentro de 3 días', 'miles'),
]


@pytest.mark.parametrize("text,confusable", _SPAN_ELSEWHERE)
def test_span_elsewhere(text, confusable):
    r = parse(text)
    assert r is not None, f"{text!r} should bind its genuine temporal part"
    assert confusable in r[1], (
        f"confusable {confusable!r} should stay in remainder {r[1]!r}")
