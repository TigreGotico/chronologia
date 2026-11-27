# -*- coding: utf-8 -*-
"""Danish time-of-day dayparts: formiddag, eftermiddag, aften and nat.

nat ``[00:00, 05:00)``, morgen ``[05:00, 10:00)``, formiddag
``[10:00, 12:00)``, eftermiddag ``[12:00, 18:00)``, aften ``[18:00, 24:00)``.
Bare "morgen" is the morning (en.wiktionary "morgen", Danish noun); only
"i morgen" and "imorgen" are tomorrow.

The boundaries are the Unicode CLDR 47 day-period rules for locale ``da``
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
    ('i formiddag', AstroDate(2017, 6, 27, 10, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('i eftermiddag', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('imorgen eftermiddag', AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 18, 0)),
    ('i aften', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('igår aften', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('imorgen aften', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('i nat', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 5, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_bare_morgen_is_the_morning_band():
    _band('morgen', AstroDate(2017, 6, 27, 5, 0), AstroDate(2017, 6, 27, 10, 0))


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'god aften',
    'aften',
    'nat nat',
])
def test_adversarial_never_raises(text):
    """Garbage, bare day-part words and non-temporal uses must be survivable.

    The contract is that nothing here raises; a sentence may legitimately bind
    a band or bind nothing, and both are recorded in the cases that assert a
    result. What must never happen is an exception escaping the parser.
    """
    parse(text)


# Den Danske Ordbog, "morgen", expression "i morgen tidlig": "på et tidligt
# tidspunkt den følgende dags morgen".  The first row is DDO's own citation
# (Berlingske Tidende, 1998).
@pytest.mark.parametrize("text", [
    'i morgen tidlig',
    'Mødet mellem de tre ledere bliver indledt i morgen tidlig',
])
def test_i_morgen_tidlig_is_tomorrow_morning(text):
    s = span(text)
    assert (s.start, s.end) == (AstroDate(2017, 6, 28, 5, 0),
                                AstroDate(2017, 6, 28, 10, 0))


@pytest.mark.parametrize("text", ['for tidlig', 'han kom tidlig'])
def test_bare_tidlig_is_no_date(text):
    assert parse(text) is None
