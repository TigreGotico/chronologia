# -*- coding: utf-8 -*-
"""Spelled feminine-ordinal clock hours, hours 1..12 x every daypart particle.

Arabic tells clock hours with the FEMININE ordinal -- الثامنة ("the eighth
[hour]") is eight o'clock, not the cardinal ثمانية.  A daypart particle selects
the meridiem: صباحا (morning/AM), مساءً (evening/PM), ظهرا (noon/PM), ليلا
(night/PM).  So الثامنة صباحا == 08:00 and الثامنة مساءً == 20:00.

The gold is computed by INDEPENDENT arithmetic here -- the 12->24 hour shift and
the prefer_future minute-wide roll are re-derived, never read back from the
parser.  Forms confirmed idiomatic MSA (feminine ordinal hour + daypart)."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

# feminine ordinal hour surface -> 12-hour clock number
_HOURS = {
    "الواحدة": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5,
    "السادسة": 6, "السابعة": 7, "الثامنة": 8, "التاسعة": 9, "العاشرة": 10,
    "الحادية عشرة": 11, "الثانية عشرة": 12,
}
# daypart particle -> meridiem: True == PM (off +12), False == AM (off 0)
_DAYPARTS = {"صباحا": False, "مساءً": True, "ظهرا": True, "ليلا": True}


def _gold(h12, pm):
    """The independent 12->24 hour shift, mirroring the meridiem policy:
    AM leaves 1..11 alone and sends 12 to 0 (midnight); PM sends 1..11 to
    13..23 and leaves 12 (noon) alone."""
    if pm:
        h24 = h12 + 12 if h12 < 12 else 12
    else:
        h24 = 0 if h12 == 12 else h12
    dt = ANCHOR.replace(hour=h24, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:                      # prefer_future roll onto tomorrow
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("hour_word,h12", list(_HOURS.items()))
@pytest.mark.parametrize("part,pm", list(_DAYPARTS.items()))
def test_spelled_hour_x_daypart(hour_word, h12, part, pm):
    text = "%s %s" % (hour_word, part)
    assert start(text) == _gold(h12, pm)


@pytest.mark.parametrize("hour_word,h12", list(_HOURS.items()))
def test_spelled_hour_after_oclock_marker(hour_word, h12):
    """الساعة (o'clock) alone licenses the bare spelled hour -> H:00, no
    meridiem shift."""
    dt = ANCHOR.replace(hour=h12, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start("الساعة %s" % hour_word) == ad(dt)
