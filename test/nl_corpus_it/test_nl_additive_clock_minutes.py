# -*- coding: utf-8 -*-
"""Additive spoken-clock minutes for Italian: "<ora> e <N>" folds the spoken
cardinal after the "e" connector into the MINUTE slot ("le sette e venti" ==
07:20), beyond the fixed quarter/half vocabulary ("e mezza"/"e un quarto").

Gold is independent: the expected minute is the plain integer the spoken
amount names, rolled to the coming day by the construction's prefer_future.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

#: (hour word, hour value).
_HOURS = [
    ("due", 2), ("tre", 3), ("quattro", 4), ("cinque", 5), ("sei", 6),
    ("sette", 7), ("otto", 8), ("nove", 9), ("dieci", 10), ("undici", 11),
]

#: (minute phrase, minute value) -- the round/simple spoken minutes the shared
#: Italian number back-end reads (it does not spell out one-word 21..29).
_MINUTES = [
    ("cinque", 5), ("dieci", 10), ("venti", 20), ("trenta", 30),
    ("quaranta", 40), ("cinquanta", 50),
]


@pytest.mark.parametrize("hw,hv", _HOURS)
@pytest.mark.parametrize("mw,mv", _MINUTES)
def test_additive_minutes_sweep(hw, hv, mw, mv):
    dt = ANCHOR.replace(hour=hv, minute=mv, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start(f"le {hw} e {mw}") == ad(dt)
