# -*- coding: utf-8 -*-
"""Oracle sweep: relative day x CLDR daypart band composition.

Deictic day (besok +1, lusa +2, kemarin -1, "hari ini" 0, "kemarin lusa" -2)
composed with a time-of-day band (pagi 00-10, siang 10-15, sore 15-18, malam
18-24, per locale id). Gold = the band window on the offset day, by independent
arithmetic. Anchor is the mission Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, start_end

A = datetime(2017, 6, 27, 13, 4)

#: (start_h, start_m) .. (end_h, end_m); 24 => next midnight
_BAND = {
    "pagi": ((0, 0), (10, 0)),
    "siang": ((10, 0), (15, 0)),
    "sore": ((15, 0), (18, 0)),
    "malam": ((18, 0), (24, 0)),
}
_OFF = {"besok": 1, "lusa": 2, "kemarin": -1, "hari ini": 0, "kemarin lusa": -2}


def _cases():
    out = []
    for rel, off in _OFF.items():
        day = (A + timedelta(days=off)).date()
        base = datetime(day.year, day.month, day.day)
        for bw, ((h1, m1), (h2, m2)) in _BAND.items():
            s = base + timedelta(hours=h1, minutes=m1)
            e = base + timedelta(hours=h2, minutes=m2)  # 24h -> next midnight
            out.append((f"{rel} {bw}",
                        AstroDate(s.year, s.month, s.day, s.hour, s.minute),
                        AstroDate(e.year, e.month, e.day, e.hour, e.minute)))
    return out


@pytest.mark.parametrize("text,s,e", _cases())
def test_relative_daypart(text, s, e):
    assert start_end(text, A) == (s, e)
