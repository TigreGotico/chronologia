# -*- coding: utf-8 -*-
"""Spanish time-of-day dayparts: manana, tarde, noche and madrugada.

Spanish runs one ``tarde`` from noon to eight in the evening, across what
English splits into afternoon and evening, and names the small hours
``madrugada``, which English cannot say in one word: madrugada
``[00:00, 06:00)``, manana ``[06:00, 12:00)``, tarde ``[12:00, 20:00)``, noche
``[20:00, 24:00)``.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``es``
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
    ('esta mañana', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('esta manana', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('ayer por la mañana', AstroDate(2017, 6, 26, 6, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('esta tarde', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 20, 0)),
    ('ayer por la tarde', AstroDate(2017, 6, 26, 12, 0), AstroDate(2017, 6, 26, 20, 0)),
    ('mañana por la tarde', AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 20, 0)),
    ('esta noche', AstroDate(2017, 6, 27, 20, 0), AstroDate(2017, 6, 28)),
    ('de madrugada', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 6, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_named_day_is_still_a_whole_day():
    """"manana" is both the morning and tomorrow, and the bare word keeps the
    tomorrow reading: the day-part is licensed only by an article, a
    demonstrative or "de" in front of it, so no phrase can quietly lose a day."""
    s = span('mañana')
    assert (s.start, s.end) == (AstroDate(2017, 6, 28), AstroDate(2017, 6, 29))


@pytest.mark.parametrize("text", [
    'llegó tarde',
    'llegó tarde a la reunión',
    'buenas tardes',
])
def test_non_temporal_use_binds_nothing(text):
    """Without a licensing article, demonstrative or "de", the bare noun is
    left alone -- which is what keeps the adverbial "llego tarde" ("arrived
    late") from being read as this afternoon."""
    assert parse(text) is None


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'mañana mañana mañana',
    'tarde',
    'la la la tarde tarde',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)
