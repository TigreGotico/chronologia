# -*- coding: utf-8 -*-
"""Greek time-of-day dayparts: πρωί, απόγευμα, βράδυ, νύχτα.

Greek carves the day into four bands whose boundaries are the Unicode CLDR
47 day-period rules for locale ``el``, collapsed into chronologia's own
four-band model (morning = CLDR morning1+morning2, afternoon =
afternoon1+afternoon2, evening = evening1, night = night1 joined with the
00:00 night2 row): πρωί ``[04:00, 12:00)``, απόγευμα ``[12:00, 17:00)``,
βράδυ ``[17:00, 20:00)``, νύχτα ``[20:00, 04:00)`` (crossing midnight).
These boundaries differ from chronologia's English default (06/12/18/21) at
every edge, which is what the adversarial case below pins.

The daypart noun appears bare, adverbially ("πρωί" -- "in the morning"), and
after the definite article ("το πρωί", "το απόγευμα", "το βράδυ", "τη
νύχτα" -- νύχτα is feminine, taking "τη" rather than the neuter "το"). On
``dev`` these phrases returned ``None`` -- ``el`` shipped zero
``daypart_*.voc`` files even though the CLDR-cited boundary rows already
existed in :mod:`chronologia.dayparts`.

Anchor: Tuesday 2017-06-27 13:04. Every band carries ``BASIS_RECONSTRUCTED``
-- a day-part is a cultural boundary, not a clock reading the speaker gave.
"""
import pytest

from chronologia.astrodate import BASIS_RECONSTRUCTED

from ._corpus import ANCHOR, AstroDate, parse, span  # noqa: F401


def _band(text, start, end):
    s = span(text)
    assert (s.start, s.end) == (start, end), f"{text!r} resolved to {s}"
    assert s.basis == BASIS_RECONSTRUCTED, f"{text!r} basis {s.basis!r}"


_BANDS = [
    ('το πρωί', AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('πρωί', AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('το απόγευμα', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 17, 0)),
    ('απόγευμα', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 17, 0)),
    ('το βράδυ', AstroDate(2017, 6, 27, 17, 0), AstroDate(2017, 6, 27, 20, 0)),
    ('βράδυ', AstroDate(2017, 6, 27, 17, 0), AstroDate(2017, 6, 27, 20, 0)),
    ('τη νύχτα', AstroDate(2017, 6, 27, 20, 0), AstroDate(2017, 6, 28, 4, 0)),
    ('νύχτα', AstroDate(2017, 6, 27, 20, 0), AstroDate(2017, 6, 28, 4, 0)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


def test_daypart_not_default_band():
    """Regression pin for the filename-suffix trap: a Greek band file that
    lands on the DEFAULT key (``daypart_morning.voc`` instead of
    ``daypart_morning_el.voc``) would silently resolve to chronologia's
    English default (06:00, not CLDR el's 04:00). Assert against the
    default row's boundary to catch that silent fallback.
    """
    s = span('το πρωί')
    assert s.start == AstroDate(2017, 6, 27, 4, 0)
    assert s.start != AstroDate(2017, 6, 27, 6, 0)  # the default row's start


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'καλημέρα',
])
def test_adversarial_never_raises(text):
    """Garbage input must be survivable -- nothing raises."""
    parse(text)
