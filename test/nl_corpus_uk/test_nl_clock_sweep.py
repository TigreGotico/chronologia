# -*- coding: utf-8 -*-
"""Digit clock sweep (uk): "HH:MM" -> that minute-wide instant.

A bare clock time binds to the anchor day, rolling to the next day when the
named time is earlier than the anchor (13:04).  The expected instant is pure
arithmetic on the anchor, independent of the parser.  Anchor Tue 2017-06-27
13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _clk(h, mi):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


_TIMES = []
for _h in range(0, 24, 2):
    for _mi in (0, 15, 30, 45):
        _TIMES.append((_h, _mi))
# a couple of exact boundaries around the anchor minute
_TIMES += [(13, 4), (13, 5), (13, 3), (0, 0), (23, 59), (12, 0)]


@pytest.mark.parametrize("h,mi", _TIMES)
def test_clock(h, mi):
    phrase = f"{h:02d}:{mi:02d}"
    assert start(phrase) == _clk(h, mi), phrase
