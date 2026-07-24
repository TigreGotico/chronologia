# -*- coding: utf-8 -*-
"""Catalan time-of-day dayparts: mati, tarda, vespre, nit and matinada.

Catalan cuts the day six ways and the tarda does not start at noon: an
hour-wide ``migdia`` holds 12:00 to 13:00 first, and a ``vespre`` sits between
the tarda and the nit where Spanish runs one tarde straight through. Bands
here: matinada ``[00:00, 06:00)``, mati ``[06:00, 12:00)``, tarda
``[13:00, 19:00)``, vespre ``[19:00, 21:00)``, nit ``[21:00, 24:00)``. The
migdia band is registered but has no vocabulary, because "migdia" is already
this locale's word for the noon instant and must keep that reading.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``ca``
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
    ('aquest matí', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('demà al matí', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('al matí ben aviat', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('aquesta tarda', AstroDate(2017, 6, 27, 13, 0), AstroDate(2017, 6, 27, 19, 0)),
    ('ahir a la tarda', AstroDate(2017, 6, 26, 13, 0), AstroDate(2017, 6, 26, 19, 0)),
    ('aquest vespre', AstroDate(2017, 6, 27, 19, 0), AstroDate(2017, 6, 27, 21, 0)),
    ('ahir a la nit', AstroDate(2017, 6, 26, 21, 0), AstroDate(2017, 6, 27)),
    ('de matinada', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"dema" is a word of its own, so no Catalan day-part shadows tomorrow."""
    s = span('demà')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'bona nit',
    'nit',
    'tarda tarda tarda',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
