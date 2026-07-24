# -*- coding: utf-8 -*-
"""Norwegian Nynorsk time-of-day dayparts: foremiddag, ettermiddag, kveld, natt.

natt ``[00:00, 06:00)``, morgon ``[06:00, 10:00)``, foremiddag
``[10:00, 12:00)``, ettermiddag ``[12:00, 18:00)``, kveld ``[18:00, 24:00)``.
Nynorsk shares the Bokmal boundaries and differs in the words, so the bands
are the chart's Norwegian rows and the vocabulary is Nynorsk. The morgon band
is registered without vocabulary: this locale lists a bare "morgon" as
tomorrow.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``no``
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
    ('i føremiddag', AstroDate(2017, 6, 27, 10, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('i ettermiddag', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('imorgon ettermiddag', AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 18, 0)),
    ('i kveld', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('igår kveld', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('imorgon kveld', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('i natt', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """This locale lists a bare "morgon" as tomorrow, so the morgon band ships
    no vocabulary and the bare word keeps the day reading."""
    s = span('morgon')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'god kveld',
    'kveld',
    'natt natta',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
