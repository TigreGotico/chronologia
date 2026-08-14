# -*- coding: utf-8 -*-
"""French time-of-day dayparts: matin, soir and nuit.

French opens the matin at four in the morning, two hours before English, and
runs the soir to midnight with no band between it and the nuit, which is the
small hours: nuit ``[00:00, 04:00)``, matin ``[04:00, 12:00)``, soir
``[18:00, 24:00)``. The apres-midi band ``[12:00, 18:00)`` is covered in
``test_nl_r165_apres_midi.py`` instead of here.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``fr``
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
    ('ce matin', AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('demain matin', AstroDate(2017, 6, 28, 4, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('hier matin', AstroDate(2017, 6, 26, 4, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('ce soir', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('hier soir', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('demain soir', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('cette nuit', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 4, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"demain" is a word of its own, so no French day-part shadows tomorrow."""
    s = span('demain')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'bonne nuit',
    'matin',
    'soir soir soir',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
