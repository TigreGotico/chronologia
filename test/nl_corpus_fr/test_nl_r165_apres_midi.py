# -*- coding: utf-8 -*-
"""R165: French "après-midi" (afternoon) daypart was registered as a band
(``chronologia/dayparts.py``, ``[12:00, 18:00)``) but shipped no
``daypart_*.voc`` surface, so it stranded as remainder instead of composing
with a weekday the way "matin"/"soir" already do. Gold band bounds are the
CLDR fr transcription already used by ``test_nl_daypart.py``; the weekday
math is the shared ANCHOR (Tuesday 2017-06-27 13:04) rolled forward to the
next Monday by hand.
"""
from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, start_end


def test_bare_apres_midi_band():
    assert start_end("après-midi") == (
        AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day, 12, 0),
        AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day, 18, 0),
    )


def test_weekday_apres_midi_composes():
    # ANCHOR is Tuesday 2017-06-27; the next Monday is 2017-07-03.
    assert start_end("lundi après-midi") == (
        AstroDate(2017, 7, 3, 12, 0),
        AstroDate(2017, 7, 3, 18, 0),
    )


def test_ascii_apres_midi_composes():
    assert start_end("lundi apres-midi") == (
        AstroDate(2017, 7, 3, 12, 0),
        AstroDate(2017, 7, 3, 18, 0),
    )


def test_control_weekday_matin_composes():
    """Sibling daypart this file's fix must not regress."""
    assert start_end("lundi matin") == (
        AstroDate(2017, 7, 3, 4, 0),
        AstroDate(2017, 7, 3, 12, 0),
    )


def test_control_weekday_soir_composes():
    assert start_end("lundi soir") == (
        AstroDate(2017, 7, 3, 18, 0),
        AstroDate(2017, 7, 4, 0, 0),
    )
