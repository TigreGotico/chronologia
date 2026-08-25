# -*- coding: utf-8 -*-
"""Serbian time-of-day dayparts (CLDR 47 day-period bands, locale sr).

The four ``daypart_*_sr.voc`` files (ujutru/ујутру, popodne/поподне,
uveče/увече, noću/ноћу) had no ``sr`` row in chronologia/dayparts.py's band
table, so the vocabulary matched but the band lookup found nothing and the
phrase fell through unresolved. This file pins the CLDR rows (morning1
06:00-12:00, afternoon1 12:00-18:00, evening1 18:00-21:00, night1
21:00-06:00, wrapping) in both scripts, plus the deictic composition with a
named day. Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import BASIS_RECONSTRUCTED

from ._corpus import AstroDate, nomatch, parse, span, start  # noqa: F401

#: pinned to the mission anchor (Tuesday 13:04) so the asserted bands are
#: reproducible regardless of the corpus helper's own default anchor.
A = datetime(2017, 6, 27, 13, 4)


_BANDS = [
    ('ujutru', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('ујутру', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('popodne', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('поподне', AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ('uveče', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 27, 21, 0)),
    ('увече', AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 27, 21, 0)),
    # night wraps into the next civil day
    ('noću', AstroDate(2017, 6, 27, 21, 0), AstroDate(2017, 6, 28, 6, 0)),
    ('ноћу', AstroDate(2017, 6, 27, 21, 0), AstroDate(2017, 6, 28, 6, 0)),
    ('danas ujutru', AstroDate(2017, 6, 27, 6, 0), AstroDate(2017, 6, 27, 12, 0)),
    ('juče uveče', AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 26, 21, 0)),
]


@pytest.mark.parametrize("text,start_,end_", _BANDS)
def test_daypart_band(text, start_, end_):
    s = span(text, A)
    assert (s.start, s.end) == (start_, end_), f"{text!r} resolved to {s}"
    assert s.basis == BASIS_RECONSTRUCTED, f"{text!r} basis {s.basis!r}"


@pytest.mark.parametrize("text", ['', '   ', '!!!', 'zzz qqq', '1234567890'])
def test_adversarial_never_raises(text):
    parse(text, A)


# -- guards: shipped Serbian behaviours the daypart fix must not touch ------

@pytest.mark.parametrize("phrase", ["dve nedelja", "две недеља"])
def test_counted_nedelja_still_refuses(phrase):
    nomatch(phrase, A)


@pytest.mark.parametrize("phrase", ["nedelja", "недеља"])
def test_bare_nedelja_still_names_sunday(phrase):
    s = start(phrase, A)
    assert s.weekday() == 6, f"{phrase!r} resolved to {s}, not a Sunday"


def test_pola_cetiri_still_three_thirty():
    s = start("pola četiri", A)
    assert (s.hour, s.minute) == (3, 30)
