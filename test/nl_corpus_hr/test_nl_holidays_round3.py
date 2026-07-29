# -*- coding: utf-8 -*-
"""Round-3 NL holidays for Croatian: national fixed-date public holidays added
in the round-3 sweep, each named with an explicit year, gold by independent
calendar arithmetic. Every case resolves to the single civil day
[Y-M-D 00:00, Y-M-D+1 00:00). Anchor 2017-06-27 13:04.
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, span, start

_YEARS = (1918, 1955, 1991, 2003, 2017, 2024, 2036, 2050, 2077, 2099)
_HOLIDAYS = [
    ('praznik rada', 5, 1),
    ('dan državnosti', 5, 30),
    ('dan antifašističke borbe', 6, 22),
    ('dan pobjede', 8, 5),
    ('velika gospa', 8, 15),
    ('sveti stjepan', 12, 26),
]
_CASES = [(f"{name} {y}", y, m, d)
          for name, m, d in _HOLIDAYS for y in _YEARS]


@pytest.mark.parametrize("text,y,m,d", _CASES, ids=[c[0] for c in _CASES])
def test_round3_fixed_holiday(text, y, m, d):
    assert start(text) == AstroDate(y, m, d), text
    assert span(text).width == timedelta(days=1)
