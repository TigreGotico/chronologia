# -*- coding: utf-8 -*-
"""Halves of a NAMED MONTH (de): "erste Hälfte von August" -> Aug 1..Aug 16
12:00, the exact arithmetic midpoint (same convention as ``month_fuzzy``'s
early/mid/late thirds). Before this order existed, month NAMES were not
``SCOPE_UNIT`` tokens, so ``half_period`` never matched them and the bare
MONTH construction won the shared span -- "erste Hälfte von" stranded in the
remainder (a silent-wrong, too-wide answer). Edges hand-derived (anchor
2017-06-27). Controls guard the year-scoped half and the bare month, which
must stay unchanged."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end

_CASES = [
    ('erste Hälfte von August', 2017, 8, 1, 0, 2017, 8, 16, 12),
    ('zweite Hälfte von August', 2017, 8, 16, 12, 2017, 9, 1, 0),
    ('erste Hälfte von Februar', 2017, 2, 1, 0, 2017, 2, 15, 0),
    ('erste Hälfte von August 2027', 2027, 8, 1, 0, 2027, 8, 16, 12),
]

@pytest.mark.parametrize("text,sy,sm,sd,sh,ey,em,ed,eh", _CASES)
def test_half_of_month(text, sy, sm, sd, sh, ey, em, ed, eh):
    s, e = start_end(text)
    assert s == AstroDate(sy, sm, sd, sh)
    assert e == AstroDate(ey, em, ed, eh)


def test_half_of_year_unchanged():
    assert start_end('erste Hälfte 2027') == (
        AstroDate(2027, 1, 1), AstroDate(2027, 7, 1))


def test_bare_month_unchanged():
    assert start_end('August') == (AstroDate(2017, 8, 1), AstroDate(2017, 9, 1))
