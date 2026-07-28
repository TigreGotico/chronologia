# -*- coding: utf-8 -*-
"""Kabyle weekday + daypart ("<weekday> <part-of-day>").

A weekday names its next strictly-future occurrence (prefer-future, as for a
bare weekday), and the trailing daypart narrows that day to its band. Anchor
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


def _next_weekday(idx):
    ahead = (idx - _BASE.weekday()) % 7 or 7
    return _BASE + timedelta(days=ahead)


_CASES = [
    ("%s %s" % (WD[i], p), i, p)
    for i in WD for p in BANDS
]


@pytest.mark.parametrize("text,idx,part", _CASES)
def test_weekday_daypart(text, idx, part):
    day = _next_weekday(idx)
    s, e = _band(day, part)
    sp = span(text)
    assert sp.start_datetime == s
    assert sp.end_datetime == e
