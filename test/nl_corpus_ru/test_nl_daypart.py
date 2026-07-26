# -*- coding: utf-8 -*-
"""Russian time-of-day dayparts: утро, день, вечер, ночь.

Russian carves the day into four bands whose boundaries are the Unicode
CLDR 47 day-period rules for locale ``ru``: ночь ``[00:00, 04:00)``, утро
``[04:00, 12:00)``, день ``[12:00, 18:00)``, вечер ``[18:00, 24:00)``. Unlike
English, the evening (вечер) runs all the way to midnight and the night
(ночь) is the small hours, not a midnight-crosser -- exactly the German
Abend/Nacht shape.

The daypart word appears as the instrumental adverb (утром "in the morning",
днём "in the afternoon/by day", вечером "in the evening", ночью "at night"),
which is the form these deictic phrases actually use. On ``dev`` these phrases
SILENTLY returned the whole day and stranded the daypart word ("сегодня утром"
-> whole 2017-06-27, "утром" dropped); this file pins the correct band.

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
    # this morning / yesterday evening / tomorrow afternoon -- the three the
    # mission names, plus the night band and a bare daypart (today's band).
    ('сегодня утром', AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('вчера утром', AstroDate(2017, 6, 26, 4, 0), AstroDate(2017, 6, 26, 12, 0)),
    ('завтра утром', AstroDate(2017, 6, 28, 4, 0), AstroDate(2017, 6, 28, 12, 0)),
    ('сегодня днём', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('завтра днём', AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 18, 0)),
    ('сегодня вечером', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
    ('вчера вечером', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 27)),
    ('завтра вечером', AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 29)),
    ('сегодня ночью', AstroDate(2017, 6, 27, 0, 0), AstroDate(2017, 6, 27, 4, 0)),
    ('вчера ночью', AstroDate(2017, 6, 26, 0, 0), AstroDate(2017, 6, 26, 4, 0)),
    # bare instrumental adverb -> today's band
    ('утром', AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('вечером', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 28)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    _band(text, start, end)


@pytest.mark.parametrize("text", [
    '',
    '   ',
    '!!!',
    'asdf qwer zxcv',
    '1234567890',
    'доброе утро',
    'днём',
    'ночью',
])
def test_adversarial_never_raises(text):
    """Garbage and bare daypart adverbs must be survivable -- nothing raises."""
    parse(text)
