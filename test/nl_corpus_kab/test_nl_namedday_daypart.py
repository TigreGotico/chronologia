# -*- coding: utf-8 -*-
"""Kabyle named-day + daypart ("<yesterday|today|tomorrow> <part-of-day>").

The named-day word fixes the calendar day (assa = today, iḍelli = yesterday,
azekka = tomorrow) and the trailing daypart narrows it to its band. Anchor Tue
2017-06-27; gold from independent arithmetic. Surfaces attested by native
speaker athmanemokraoui (#265).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, span
from .test_nl_daypart_matrix import BANDS, _band

# named-day surface -> day offset from anchor
ND = {"assa": 0, "iḍelli": -1, "azekka": 1}

_BASE = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)

_CASES = [
    ("%s %s" % (nd, p), off, p)
    for nd, off in ND.items() for p in BANDS
]


@pytest.mark.parametrize("text,off,part", _CASES)
def test_namedday_daypart(text, off, part):
    day = _BASE + timedelta(days=off)
    s, e = _band(day, part)
    sp = span(text)
    assert sp.start_datetime == s
    assert sp.end_datetime == e
