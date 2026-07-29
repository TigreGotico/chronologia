# -*- coding: utf-8 -*-
"""Aragonese "nueyt" (night) clock meridiem: a midnight-crossing BAND, not a
uniform +12 PM shift.  "la una de nueyt" is 01:00 (not 13:00) and "las once
de nueyt" is 23:00, with small hours 1..5 staying AM, evening hours 6..11
becoming PM, and twelve landing on midnight.  Gold is computed by
independent arithmetic (h if h <= 5 else h + 12, h == 12 -> 0), never read
back from the parser -- this is exactly the bug: before the fix, the pm.voc
union of "nueyt" applied a flat +12 and turned "la una de nueyt" into 13:00.

AN is Ibero-Romance and inherits the same madrugada band [00:00, 06:00) --
hence the 5|6 cut -- as the es/ca/pt siblings (chronologia/locale/es/
clock_meridiem_night.voc); native confirmation for Aragonese specifically is
still open, tracked in issue #266.
"""
import pytest

from ._corpus import start

_NUM = [
    ("una", 1), ("dos", 2), ("tres", 3), ("cuatro", 4), ("cinco", 5),
    ("seis", 6), ("siete", 7), ("ueito", 8), ("nueu", 9), ("diez", 10),
    ("once", 11), ("doce", 12),
]


def _gold(h):
    if h == 12:
        return 0
    if h <= 5:
        return h
    return h + 12


@pytest.mark.parametrize("nw,h", _NUM)
def test_nueyt_matrix(nw, h):
    assert start(f"a las {nw} de nueyt").hour == _gold(h)


@pytest.mark.parametrize("text,h", [
    ("la una de nueyt", 1), ("las cinco de nueyt", 5),
    ("las seis de nueyt", 18), ("las once de nueyt", 23),
    ("las doce de nueyt", 0),
])
def test_nueyt_spot(text, h):
    assert start(text).hour == h
