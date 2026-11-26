# -*- coding: utf-8 -*-
"""A daypart before or after a led clock range puts its bare hours in the band.

"heute Nachmittag von zwei bis sechs Uhr" names 14:00 to 18:00 of the anchor
day: the daypart picks the afternoon half for the bare hours "zwei" and
"sechs".  Gold is plain arithmetic: hour h in the afternoon is h + 12, a
clock point end is end-exclusive by one minute.  Anchor: Tuesday
27 June 2017, 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def _pm(start, end):
    """The afternoon span from bare hour ``start`` to bare hour ``end``."""
    return (datetime(2017, 6, 27, start + 12, 0),
            datetime(2017, 6, 27, end + 12, 1))


ROWS = [
    ("en", "The book swap runs this afternoon from two to three.", 2, 3),
    ("de", "Die Probe im Gemeindesaal dauert heute Nachmittag von zwei bis "
           "sechs Uhr, also bring bitte genug Wasser mit.", 2, 6),
    ("de", "Die Sprechstunde findet heute Nachmittag von drei bis sechs Uhr "
           "statt.", 3, 6),
    ("es", "La reunión con los vecinos durará esta tarde de tres a cinco, "
           "así que trae algo de picar.", 3, 5),
    ("ca", "La fira estarà oberta aquesta tarda de cinc a vuit.", 5, 8),
    ("el", "Η συνάντηση θα διαρκέσει σήμερα το απόγευμα από τις δύο έως τις "
           "έξι.", 2, 6),
    ("ro", "Atelierul se desfășoară în această după-amiază, de la ora patru "
           "până la ora opt.", 4, 8),
    ("sv", "Loppisen pågår i eftermiddag från klockan två till sex.", 2, 6),
]


@pytest.mark.parametrize("lang,text,start,end", ROWS)
def test_daypart_frames_clock_range(lang, text, start, end):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.span.end) == _pm(start, end)


def test_frame_leaves_the_rest_in_remainder():
    r = extract_timespan("Die Probe dauert heute Nachmittag von zwei bis "
                         "sechs Uhr, also komm.", "de", ANCHOR)
    assert "Nachmittag" not in r.remainder
    assert "Probe" in r.remainder


OPEN = [
    ("fr", "La réunion se tiendra cet après-midi de une heure à cinq heures "
           "dans la grande salle.", 1, 5),
    ("ms", "Mesyuarat itu akan berlangsung petang ini dari pukul tiga hingga "
           "pukul empat.", 3, 4),
    ("hu", "Ma délután öttől nyolcig tart a bemutató.", 5, 8),
]


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="TigreGotico/chronologia#1460: range not read")
@pytest.mark.parametrize("lang,text,start,end", OPEN)
def test_daypart_frames_clock_range_open(lang, text, start, end):
    r = extract_timespan(text, lang, ANCHOR)
    assert r is not None
    assert (r.span.start, r.span.end) == _pm(start, end)
