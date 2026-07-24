# -*- coding: utf-8 -*-
"""The four temperate seasons -- this/next/last, and a season of a year.

Kamus Dewan lists the four under "musim": musim bunga (semi),
musim panas, musim luruh (gugur, rontok) and musim dingin (sejuk), the
last of these glossed as the cold season of cold-weather countries, so
the words name the temperate seasons Malaysia itself does not have.

Meteorological seasons, three whole months wide, northern hemisphere.
"this" is the occurrence the anchor stands in, "depan" the first one
still to begin and "lepas" the most recent one already over, so from a
July anchor "musim panas depan" is next year's June.  Expected spans come
from the calendar, never pinned from the engine.
"""
import pytest

from chronologia.astrodate import AstroDate

from ._corpus import parse, span, nomatch

CASES = [
    ('musim panas ini', 2026, 6),
    ('musim panas depan', 2027, 6),
    ('musim panas lepas', 2025, 6),
    ('musim bunga depan', 2027, 3),
    ('musim luruh lepas', 2025, 9),
    ('musim sejuk ini', 2026, 12),
    ('musim rontok ini', 2026, 9),
    ('musim dingin depan', 2026, 12),
    ('Saya ke Jepun musim luruh ini', 2026, 9),
    ('musim panas 2018', 2018, 6),
    ('musim panas', 2026, 6),
]

#: the wet/dry pair the country actually lives by is deliberately absent:
#: it is a two-season year the engine has no slot for, and guessing a
#: three-month block for it would be a confident wrong answer.
_LOCAL_SEASONS = [
    'musim hujan',
    'musim kemarau',
    'musim tengkujuh',
]

_FUZZ = [
    'musim musim panas',
    'musim panas musim sejuk',
    'musim panas 🎉',
    'panas',
    'musim',
    'musim panas depan lepas ini',
]


@pytest.mark.parametrize("text,y,m", CASES)
def test_season(text, y, m):
    sp = span(text)
    assert sp.start == AstroDate(y, m, 1)
    assert sp.end == AstroDate(y + (m + 3) // 13, (m + 2) % 12 + 1, 1)


@pytest.mark.parametrize("text", _LOCAL_SEASONS)
def test_wet_and_dry_seasons_are_not_modelled(text):
    nomatch(text)


@pytest.mark.parametrize("text", _FUZZ)
def test_never_raises(text):
    parse(text)
