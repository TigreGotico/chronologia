# -*- coding: utf-8 -*-
"""Galician time-of-day dayparts: mana, tarde, noite and madrugada.

The Galician tarde is the widest of the Romance afternoons -- eight hours,
running to nine at night: madrugada ``[00:00, 06:00)``, mana
``[06:00, 12:00)``, tarde ``[13:00, 21:00)``, noite ``[21:00, 24:00)``. The
hour-wide ``mediodia`` band between them is registered but has no vocabulary,
"mediodia" being this locale's word for the noon instant.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``gl``
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
    ('esta mañá', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('pola mañá', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('de mañá', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('onte pola tarde', AstroDate(2017, 6, 26, 13, 0), AstroDate(2017, 6, 26, 21, 0)),
    ('mañá pola tarde', AstroDate(2017, 6, 28, 13, 0), AstroDate(2017, 6, 28, 21, 0)),
    ('á tarde', AstroDate(2017, 6, 27, 13, 0), AstroDate(2017, 6, 27, 21, 0)),
    ('esta noite', AstroDate(2017, 6, 27, 21, 0), AstroDate(2017, 6, 28)),
    ('de madrugada', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """The Real Academia Galega gives "mana" both senses in one entry, the
    "parte do dia" and the "dia seguinte ao de hoxe". The bare word keeps the
    tomorrow reading; the day-part fires only under an article, "de", "a" or
    "pola"."""
    s = span('mañá')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    'chegou tarde',
    'boas noites',
])
def test_non_temporal_use_binds_nothing(text):
    """Without a licensing preposition or article the bare noun binds nothing."""
    assert parse(text) is None


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'mañá mañá',
    'tarde',
    'pola pola mañá',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
