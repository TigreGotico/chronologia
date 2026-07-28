# -*- coding: utf-8 -*-
"""KNOWN BUG (strict-xfail): spelled-out clock hours do not resolve.

A digit clock hour works ("8 صباحا" -> 08:00), but the *spelled* feminine
ordinal hour الثامنة / التاسعة ("the eighth/ninth [hour]") is not recognised as
a clock reference:

    الساعة الثامنة صباحا   -> None            (expected 08:00, minute-wide)
    التاسعة صباحا          -> None            (expected 09:00, minute-wide)
    الساعة الثامنة         -> None            (expected 08:00, minute-wide)
    الثامنة مساء           -> evening band 18:00-21:00, drops "الثامنة"
                                              (expected 20:00, minute-wide)

Gold (independent arithmetic, minute-wide span with the prefer_future roll):
08:00/09:00 are still ahead of the 13:04 anchor tomorrow; 20:00 is still ahead
today.  Marked xfail(strict) so the day the parser learns spelled clock hours,
this flips to a failure and the assertions become live regression guards.

For the human reviewer: confirm the spelled feminine ordinal hour forms
(الواحدة، الثانية، الثالثة … الثانية عشرة) are the idiomatic MSA way to say
clock hours, and that meridiem particles صباحا/مساء select AM/PM as encoded."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _clk(h, mi=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.xfail(strict=True, reason="spelled clock hour الثامنة not parsed")
@pytest.mark.parametrize("text,h", [
    ("الساعة الثامنة صباحا", 8),
    ("التاسعة صباحا", 9),
    ("الساعة الثامنة", 8),
    ("الثامنة مساء", 20),
])
def test_spelled_clock_hour(text, h):
    assert start(text) == _clk(h)
