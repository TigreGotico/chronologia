# -*- coding: utf-8 -*-
"""Directional relative offsets across many magnitudes and all four units.
לפני = ago (past), בעוד = in (future).  The offset anchors on the mission
Tuesday 13:04 and preserves the clock; only the span start is pinned (the span
width is unit-dependent and out of scope here).  Gold by independent
:mod:`dateutil` arithmetic."""
import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start

_N = (2, 4, 6, 9, 20, 40)

# Hebrew plural unit noun -> relativedelta keyword
_UNITS = {
    "ימים": "days",
    "שבועות": "weeks",
    "חודשים": "months",
    "שנים": "years",
}


def _cases():
    out = []
    for noun, kw in _UNITS.items():
        for n in _N:
            delta = relativedelta(**{kw: n})
            out.append((f"בעוד {n} {noun}", ANCHOR + delta))
            out.append((f"לפני {n} {noun}", ANCHOR - delta))
    return out


@pytest.mark.parametrize("text,expected", _cases())
def test_offset_start(text, expected):
    assert start(text) == ad(expected)
