# -*- coding: utf-8 -*-
"""Turkish clock readings -- ISO HH:MM, "saat N", and daypart+hour sweeps.

ISO readings are date-agnostic here: the assertion pins only (hour, minute),
which the surface names directly.  "saat N" for an hour still ahead of the
anchor (13:04) stays on the anchor's own day.  The afternoon/evening marker
adds twelve to a bare 12-hour clock hour; the oracle applies that shift
independently.  Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start

A = datetime(2017, 6, 27, 13, 4)

# spelled hour words 1..12 (Turkish cardinals)
_HOURWORD = {
    1: "bir", 2: "iki", 3: "üç", 4: "dört", 5: "beş", 6: "altı",
    7: "yedi", 8: "sekiz", 9: "dokuz", 10: "on", 11: "on bir", 12: "on iki",
}


# -- ISO HH:MM: assert the named hour/minute -------------------------------
def _iso_cases():
    out = []
    for h in range(0, 24):
        for m in (0, 7, 15, 30, 45, 59):
            out.append((f"{h:02d}:{m:02d}", h, m))
    return out


@pytest.mark.parametrize("text,h,m", _iso_cases())
def test_iso_clock(text, h, m):
    s = start(text, A)
    assert (s.hour, s.minute) == (h, m)


# -- "saat N": numeral hour, still ahead of the anchor -> same day ----------
@pytest.mark.parametrize("h", list(range(14, 24)))
def test_saat_numeral_same_day(h):
    s = start(f"saat {h}", A)
    assert (s.year, s.month, s.day) == (2017, 6, 27)
    assert (s.hour, s.minute) == (h, 0)


# -- afternoon marker "öğleden sonra saat N" -> N + 12 (N in 1..11) ---------
@pytest.mark.parametrize("h", list(range(1, 12)))
def test_afternoon_numeral(h):
    s = start(f"öğleden sonra saat {h}", A)
    assert (s.hour, s.minute) == (h + 12, 0)


# -- "saat <word>" whole hour, morning band (1..11; 12 is noon/midnight
#    ambiguous under a morning marker, so it is left out) --------------------
@pytest.mark.parametrize("n,word",
                         [(n, w) for n, w in _HOURWORD.items() if n < 12])
def test_saat_spelled_hour(n, word):
    s = start(f"sabah saat {word}", A)
    assert s.hour == n
