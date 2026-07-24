# -*- coding: utf-8 -*-
"""Dutch time-of-day dayparts: ochtend, avond and nacht.

The avond runs to midnight and the nacht takes the small hours after it:
nacht ``[00:00, 06:00)``, ochtend ``[06:00, 12:00)``, avond
``[18:00, 24:00)``. The middag band ``[12:00, 18:00)`` is registered but has
no vocabulary: "middag" is already this locale's word for the noon instant and
must keep that reading. "vanochtend" and "vanavond" are single-word
today+band surfaces, the Dutch shape of English "tonight".

The boundaries are the Unicode CLDR 47 day-period rules for locale ``nl``
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
    ('vanochtend', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('deze ochtend', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('morgen ochtend', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('gisteren ochtend', AstroDate(2017, 6, 26, 6, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('vanavond', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('morgen avond', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('gisteren avond', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('deze nacht', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"morgen" is the Dutch for tomorrow and is not a day-part word here --
    Dutch says "ochtend" for the band -- so the two never competed."""
    s = span('morgen')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'goedenavond',
    'avond',
    'nacht nacht',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
