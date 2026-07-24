# -*- coding: utf-8 -*-
"""German time-of-day dayparts: Vormittag, Nachmittag, Abend and Nacht.

German cuts the day six ways and not one of the bands is English's
afternoon: Nacht ``[00:00, 05:00)``, Morgen ``[05:00, 10:00)``, Vormittag
``[10:00, 12:00)``, Mittag ``[12:00, 13:00)``, Nachmittag ``[13:00, 18:00)``,
Abend ``[18:00, 24:00)``. The Nachmittag opens at 13:00, after the hour-wide
Mittag, and the Abend runs to midnight, so the Nacht is the small hours.
Two bands are registered without vocabulary: "Mittag" is already this locale's
word for the noon instant, and "Morgen" is the German for tomorrow.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``de``
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
    ('heute vormittag', AstroDate(2017, 6, 27, 10, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('morgen vormittag', AstroDate(2017, 6, 28, 10, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('heute nachmittag', AstroDate(2017, 6, 27, 13, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('gestern nachmittag', AstroDate(2017, 6, 26, 13, 0), AstroDate(2017, 6, 26, 18, 0)),
    ('heute abend', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('morgen abend', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('gestern abend', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('gestern nacht', AstroDate(2017, 6, 26), AstroDate(2017, 6, 26, 5, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"Morgen" is both the morning and tomorrow. German says "heute Morgen"
    with no article, so there is no position that could license the day-part
    reading without also stealing the bare word; the morning band is therefore
    registered with no vocabulary and "morgen" stays tomorrow, whole and
    unambiguous. Losing "heute Morgen" is the honest price."""
    s = span('morgen')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'guten abend',
    'abend',
    'morgen morgen morgen',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
