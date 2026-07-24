# -*- coding: utf-8 -*-
"""Romanian time-of-day dayparts: dimineata, seara and noaptea.

Romanian is the one language of this batch whose chart rows name the same
band twice -- noapte at 00:00 and again at 22:00 -- so the two are joined into
the single wrapping night they are: noapte ``[22:00, 05:00)``, dimineata
``[05:00, 12:00)``, seara ``[18:00, 22:00)``. The dupa-amiaza band
``[12:00, 18:00)`` is registered but has no vocabulary: the tokenizer splits
the hyphen, leaving "amiaza", which is already this locale's word for noon.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``ro``
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
    ('azi dimineață', AstroDate(2017, 6, 27, 5, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('mâine dimineață', AstroDate(2017, 6, 28, 5, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('ieri dimineata', AstroDate(2017, 6, 26, 5, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('azi seara', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 27, 22, 0)),
    ('ieri seara', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 26, 22, 0)),
    ('mâine seara', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 28, 22, 0)),
    ('noaptea', AstroDate(2017, 6, 27, 22, 0), AstroDate(2017, 6, 28, 5, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"maine" is a word of its own, so no Romanian day-part shadows tomorrow."""
    s = span('mâine')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'noapte bună',
    'seara',
    'dimineata dimineata',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
