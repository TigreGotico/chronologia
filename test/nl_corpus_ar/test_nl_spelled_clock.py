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
# daypart particle -> meridiem class: "am", "pm", or "night".  NIGHT (ليل) is a
# BAND that crosses midnight -- it is NOT a uniform +12 PM shift.  صباحا is
# morning/AM; مساءً (evening) and ظهرا (noon) are plain PM; ليلا is the night
# band.  الواحدة ليلا is 01:00 (one at night), not 13:00, and الثانية عشرة ليلا
# is midnight 00:00, not noon.
_DAYPARTS = {"صباحا": "am", "مساءً": "pm", "ظهرا": "pm", "ليلا": "night"}


def _gold(h12, cls):
    """The independent 12->24 hour shift, mirroring the meridiem policy:
    AM leaves 1..11 alone and sends 12 to 0 (midnight); PM sends 1..11 to
    13..23 and leaves 12 (noon) alone; NIGHT is the midnight-crossing band --
    small hours 1..5 stay AM (01..05), evening hours 6..11 are PM (18..23), and
    twelve is midnight (00)."""
    if cls == "pm":
        h24 = h12 + 12 if h12 < 12 else 12
    elif cls == "night":
        if h12 == 12:
            h24 = 0
        elif 6 <= h12 <= 11:
            h24 = h12 + 12
        else:                            # 1..5 stay AM
            h24 = h12
    else:                                # am
        h24 = 0 if h12 == 12 else h12
    dt = ANCHOR.replace(hour=h24, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:                      # prefer_future roll onto tomorrow
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("hour_word,h12", list(_HOURS.items()))
@pytest.mark.parametrize("part,cls", list(_DAYPARTS.items()))
def test_spelled_hour_x_daypart(hour_word, h12, part, cls):
    text = "%s %s" % (hour_word, part)
    assert start(text) == _gold(h12, cls)


@pytest.mark.parametrize("hour_word,h12", list(_HOURS.items()))
def test_spelled_hour_after_oclock_marker(hour_word, h12):
    """الساعة (o'clock) alone licenses the bare spelled hour -> H:00, no
    meridiem shift."""
    dt = ANCHOR.replace(hour=h12, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start("الساعة %s" % hour_word) == ad(dt)
