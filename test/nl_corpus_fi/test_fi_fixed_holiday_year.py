# -*- coding: utf-8 -*-
"""Two flagship Finnish civic holidays now bind by name (round-2 civil days).

vappu (May Day, 1 May, the shared ``labour_day``) and itsenäisyyspäivä
(Independence Day, 6 Dec, ``finland_independence_day``) are fixed-date national
holidays. "vappu 2023" resolves to 2023-05-01 (one day) and the trailing year
is consumed cleanly -- previously the holiday word was discarded and the bare
year returned. Formerly a strict xfail; promoted to a passing regression pin.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, span, start

# holiday -> (month, day)
_FIXED = {"vappu": (5, 1), "itsenäisyyspäivä": (12, 6)}

_CASES = [
    (f"{name} {y}", datetime(y, mo, d))
    for y in (2019, 2023, 2027)
    for name, (mo, d) in _FIXED.items()
]


@pytest.mark.parametrize("text,dt", _CASES)
def test_fixed_holiday_year(text, dt):
    assert start(text) == ad(dt)
    assert span(text).width == timedelta(days=1)
