# -*- coding: utf-8 -*-
"""Portuguese time-of-day dayparts: manha, tarde, noite and madrugada.

The tarde yields to the noite at seven, an hour earlier than Spanish:
madrugada ``[00:00, 06:00)``, manha ``[06:00, 12:00)``, tarde
``[12:00, 19:00)``, noite ``[19:00, 24:00)``. European and Brazilian
Portuguese share these words and this locale serves both; the chart draws no
distinction here and neither does the vocabulary.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``pt``
(https://www.unicode.org/cldr/charts/47/supplemental/day_periods.html),
transcribed in :mod:`chronologia.dayparts`. They are *not* English's: asserting
the exact span is the whole point of this file, because a band that silently
took English's hours would still look like a working day-part.

Anchor: Tuesday 2017-06-27 13:04. Every band carries
``BASIS_RECONSTRUCTED`` -- a day-part is a cultural boundary, not a clock
reading the speaker gave.
"""
import pytest

from chronologia.astrodate import BASIS_RECONSTRUCTED

from ._corpus import ANCHOR, AstroDate, parse, span  # noqa: F401


def _band(text, start, end):
    s = span(text)
    assert (s.start, s.end) == (start, end), f"{text!r} resolved to {s}"
    assert s.basis == BASIS_RECONSTRUCTED, f"{text!r} basis {s.basis!r}"


_BANDS = [
    ('esta manhã', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('de manhã', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('pela manhã', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('ontem de manhã', AstroDate(2017, 6, 26, 6, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('amanhã de manhã', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('à tarde', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 19, 0)),
    ('esta tarde', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 19, 0)),
    ('ontem pela tarde', AstroDate(2017, 6, 26, 12, 0), AstroDate(2017, 6, 26, 19, 0)),
    ('a tarde passada', AstroDate(2017, 6, 26, 12, 0), AstroDate(2017, 6, 26, 19, 0)),
    ('a manhã seguinte', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('esta noite', AstroDate(2017, 6, 27, 19, 0), AstroDate(2017, 6, 28)),
    ('ontem à noite', AstroDate(2017, 6, 26, 19, 0), AstroDate(2017, 6, 27)),
    ('de madrugada', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"amanha" is a word of its own, so tomorrow was never at risk here; the
    case is kept so the Portuguese file guards the same contract as its neighbours."""
    s = span('amanhã')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    'chegou tarde',
    'boa noite',
    'mais vale tarde do que nunca',
])
def test_non_temporal_use_binds_nothing(text):
    """"tarde" is also the adverb "late", so the bare noun is not read as the
    band: it needs the article, "de", "a" or "por" that Portuguese actually
    says, which leaves "chegou tarde" alone."""
    assert parse(text) is None


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'manhã manhã',
    'tarde',
    'a a a tarde',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
