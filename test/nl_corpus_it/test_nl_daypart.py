# -*- coding: utf-8 -*-
"""Italian time-of-day dayparts: mattina, pomeriggio, sera and notte.

The sera holds 18:00 to midnight on its own, so the notte is the small hours
of the named day and nothing else: notte ``[00:00, 06:00)``, mattina
``[06:00, 12:00)``, pomeriggio ``[12:00, 18:00)``, sera ``[18:00, 24:00)``.
"domani notte" is therefore tomorrow 00:00-06:00, not an English-shaped night
starting the previous evening -- the case that shows the transcription is
faithful rather than translated.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``it``
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
    ('questa mattina', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('domani mattina', AstroDate(2017, 6, 28, 6, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('ieri mattina', AstroDate(2017, 6, 26, 6, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('questo pomeriggio', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('domani pomeriggio', AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 18, 0)),
    ('questa sera', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('ieri sera', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('questa notte', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
    ('domani notte', AstroDate(2017, 6, 28), AstroDate(2017, 6, 28, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"domani" is a word of its own, so no Italian day-part shadows tomorrow."""
    s = span('domani')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'buona sera',
    'notte',
    'sera sera',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
