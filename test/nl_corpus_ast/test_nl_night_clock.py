# -*- coding: utf-8 -*-
"""Asturian "nueche" (night) clock meridiem: a midnight-crossing BAND, not a
uniform +12 PM shift.  "a les cinco de la nueche" is 05:00 (not 17:00) and
"a les diez de la nueche" is 22:00, with small hours 1..5 staying AM,
evening hours 6..11 becoming PM, and twelve landing on midnight.  Gold is
computed by independent arithmetic (h if h <= 5 else h + 12, h == 12 -> 0),
never read back from the parser -- this is exactly the bug: before the fix,
the pm.voc union of "nueche" applied a flat +12 and turned "a les 5 de la
nueche" into 17:00.

AST is Ibero-Romance and inherits the same madrugada band [00:00, 06:00) --
hence the 5|6 cut -- as the es/ca/pt siblings (chronologia/locale/es/
clock_meridiem_night.voc); native confirmation for Asturian specifically is
still open, tracked in issue #266.

"una" (one) is excluded from the spelled-number matrix: "a les una ..." does
not parse in the ast grammar at all, regardless of meridiem (confirmed with
"de la tarde" too) -- a pre-existing gap unrelated to this fix.
"""
import pytest

from ._corpus import start

_NUM = [
    ("dos", 2), ("tres", 3), ("cuatro", 4), ("cinco", 5),
    ("seis", 6), ("siete", 7), ("ocho", 8), ("nueve", 9), ("diez", 10),
    ("once", 11), ("doce", 12),
]


def _gold(h):
    if h == 12:
        return 0
    if h <= 5:
        return h
    return h + 12


@pytest.mark.parametrize("nw,h", _NUM)
def test_nueche_matrix(nw, h):
    assert start(f"a les {nw} de la nueche").hour == _gold(h)


@pytest.mark.parametrize("text,h", [
    ("a les 1 de la nueche", 1), ("a les 5 de la nueche", 5),
    ("a les 6 de la nueche", 18), ("a les 11 de la nueche", 23),
    ("a les 12 de la nueche", 0),
])
def test_nueche_spot(text, h):
    assert start(text).hour == h
