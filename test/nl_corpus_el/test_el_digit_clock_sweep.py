# -*- coding: utf-8 -*-
"""Digit clock sweep HH:MM across the full 24h dial. A bare time at or before
the 13:04 anchor rolls to the next day (prefer_future); the gold is
independent arithmetic off the anchor.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


_CASES = [
    (f"{h:02d}:{mi:02d}", h, mi)
    for h in range(24) for mi in (0, 15, 30, 45)
]


@pytest.mark.parametrize("text,h,mi", _CASES)
def test_digit_clock_sweep(text, h, mi):
    assert start(text) == _next_time(h, mi)
