# -*- coding: utf-8 -*-
"""Kabyle weekday + daypart ("<weekday> <part-of-day>").

A weekday names its next occurrence, or the anchor day while the band there
has not ended, and the trailing daypart narrows that day to its band. Anchor
Tue 2017-06-27; all gold from independent arithmetic. Weekday surfaces are the
locale's weekday_*.voc tables; daypart surfaces are attested by native speaker
athmanemokraoui (#265). Bands use chronologia's default day-period convention.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, span
from .test_nl_daypart_matrix import BANDS, _band

# weekday index (Mon=0) -> Kabyle surface (weekday_N.voc)
WD = {
    0: "letnayen", 1: "ttlata", 2: "laṛebɛa", 3: "lexmis",
    4: "lǧemɛa", 5: "ssebt", 6: "lḥedd",
}

_BASE = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)


def _next_weekday(idx, part):
    """The next such weekday whose band still ends after the anchor: the
    anchor's own day when the band there has not ended."""
    ahead = (idx - _BASE.weekday()) % 7
    if ahead == 0 and _band(_BASE, part)[1] <= ANCHOR:
        ahead = 7
    return _BASE + timedelta(days=ahead)


_CASES = [
    ("%s %s" % (WD[i], p), i, p)
    for i in WD for p in BANDS
]


@pytest.mark.parametrize("text,idx,part", _CASES)
def test_weekday_daypart(text, idx, part):
    day = _next_weekday(idx, part)
    s, e = _band(day, part)
    sp = span(text)
    assert sp.start_datetime == s
    assert sp.end_datetime == e
