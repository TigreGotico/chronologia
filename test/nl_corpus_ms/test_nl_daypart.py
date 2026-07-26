# -*- coding: utf-8 -*-
"""Malay time-of-day dayparts (CLDR 47 day-period bands, locale ms).

On ``dev`` these deictic phrases SILENTLY returned the whole day and stranded
the daypart word; this file pins the correct CLDR band. Bands and the cited
single-token surfaces are wired in chronologia/dayparts.py and the
``daypart_*_ms.voc`` vocabulary. Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import BASIS_RECONSTRUCTED

from ._corpus import AstroDate, parse, span  # noqa: F401

#: pinned to the mission anchor (Tuesday 13:04) so the asserted bands are
#: reproducible regardless of the corpus helper's own default anchor.
A = datetime(2017, 6, 27, 13, 4)


_BANDS = [
    ('pagi', AstroDate(2017, 6, 27), AstroDate(2017, 6, 27, 12, 0)),
    ('semalam petang', AstroDate(2017, 6, 26, 14, 0), AstroDate(2017, 6, 26, 19, 0)),
    ('esok pagi', AstroDate(2017, 6, 28), AstroDate(2017, 6, 28, 12, 0)),
    ('malam', AstroDate(2017, 6, 27, 19, 0), AstroDate(2017, 6, 28)),
]


@pytest.mark.parametrize("text,start,end", _BANDS)
def test_daypart_band(text, start, end):
    s = span(text, A)
    assert (s.start, s.end) == (start, end), f"{text!r} resolved to {s}"
    assert s.basis == BASIS_RECONSTRUCTED, f"{text!r} basis {s.basis!r}"


@pytest.mark.parametrize("text", ['', '   ', '!!!', 'zzz qqq', '1234567890'])
def test_adversarial_never_raises(text):
    parse(text, A)
