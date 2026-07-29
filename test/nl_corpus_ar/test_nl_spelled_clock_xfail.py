# -*- coding: utf-8 -*-
"""FIXED (was strict-xfail): the spelled feminine ordinal clock hour resolves.

A digit clock hour worked ("8 صباحا" -> 08:00); the *spelled* feminine ordinal
hour الثامنة / التاسعة ("the eighth/ninth [hour]") used to be dropped and the
utterance returned None.  ``numfold_semitic._ar_clock_hour_fold`` now folds the
feminine ordinal hour الواحدة..الثانية عشرة (1..12) to a CLOCK ``H:00`` token in
an unambiguous clock context (after الساعة, or before an am/pm daypart), and the
shared daypart->meridiem shift produces the 24-hour reading:

    الساعة الثامنة صباحا   -> 08:00
    التاسعة صباحا          -> 09:00
    الساعة الثامنة         -> 08:00   (meridiem-optional CLOCK order)
    الثامنة مساء           -> 20:00

Gold (independent arithmetic, minute-wide span with the prefer_future roll):
08:00/09:00 are still ahead of the 13:04 anchor tomorrow; 20:00 is still ahead
today.  These assertions are now live regression guards."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _clk(h, mi=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h", [
    ("الساعة الثامنة صباحا", 8),
    ("التاسعة صباحا", 9),
    ("الساعة الثامنة", 8),
    ("الثامنة مساء", 20),
])
def test_spelled_clock_hour(text, h):
    assert start(text) == _clk(h)
