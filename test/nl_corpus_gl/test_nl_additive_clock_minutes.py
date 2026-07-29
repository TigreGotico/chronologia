# -*- coding: utf-8 -*-
"""Additive spoken-clock minutes for Galician: "<hora> e <N>" folds the spoken
cardinal after the "e" connector into the MINUTE slot ("ás sete e vinte" ==
07:20), beyond the fixed quarter/half vocabulary ("e media"/"e cuarto").

Gold is independent: the expected minute is the plain integer the spoken
amount names, rolled to the coming day by the construction's prefer_future.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

#: (hour word, hour value).
_HOURS = [
    ("tres", 3), ("catro", 4), ("cinco", 5), ("seis", 6), ("sete", 7),
    ("oito", 8), ("nove", 9), ("dez", 10), ("once", 11),
]

#: (minute phrase, minute value) -- spoken cardinals beyond quarter/half.
_MINUTES = [
    ("cinco", 5), ("dez", 10), ("vinte", 20), ("vinte e cinco", 25),
    ("trinta e cinco", 35), ("corenta", 40), ("cincuenta", 50),
]


@pytest.mark.parametrize("hw,hv", _HOURS)
@pytest.mark.parametrize("mw,mv", _MINUTES)
def test_additive_minutes_sweep(hw, hv, mw, mv):
    dt = ANCHOR.replace(hour=hv, minute=mv, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start(f"ás {hw} e {mw}") == ad(dt)
