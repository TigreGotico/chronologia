# -*- coding: utf-8 -*-
"""Second-pass sweep: the full hour set (1..12) x the fraction vocabulary
already proven in test_nl_clock.py ("e meia", "e quarto", "e um quarto",
"menos um quarto", "menos vinte", "menos dez"), plus the bare "em ponto"
("on the dot") suffix -- none of which were swept across every hour in the
existing files (those pin only a handful of hours each).

Additive minutes beyond the fixed quarter/half vocabulary ("e vinte", "e dez",
"e vinte e cinco" ...) were independently probed against the parser and found
NOT to be picked up -- the minute simply drops to :00 -- so that surface is
deliberately excluded here rather than mis-pinned.

"em ponto" resolves the correct hour but leaves the suffix itself unconsumed
by the grammar (probed independently); this file therefore checks ``start()``
only, exactly like the rest of test_nl_clock.py, and does not assert full
consumption for that suffix.

Anchor Tuesday 2017-06-27 13:04; every case uses the ordinary prefer_future
roll (an hour already past today lands tomorrow).
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start

_NUM = {1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis",
        7: "sete", 8: "oito", 9: "nove", 10: "dez", 11: "onze", 12: "doze"}


def _clk(hour, minute):
    dt = ANCHOR.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


def _art(h):
    return "à" if h == 1 else "às"


def _half_quarter_cases():
    out = []
    for h in range(1, 13):
        a = _art(h)
        out.append((f"{a} {_NUM[h]} e meia", h, 30))
        out.append((f"{a} {_NUM[h]} e quarto", h, 15))
        out.append((f"{a} {_NUM[h]} e um quarto", h, 15))
    return out


def _minus_cases():
    out = []
    for h in range(2, 13):
        a = _art(h)
        prev = h - 1
        out.append((f"{a} {_NUM[h]} menos um quarto", prev, 45))
        out.append((f"{a} {_NUM[h]} menos vinte", prev, 40))
        out.append((f"{a} {_NUM[h]} menos dez", prev, 50))
    return out


@pytest.mark.parametrize("text,h,mi", _half_quarter_cases())
def test_hour_sweep_additive_fraction(text, h, mi):
    assert start(text) == _clk(h, mi)


@pytest.mark.parametrize("text,h,mi", _minus_cases())
def test_hour_sweep_subtractive_fraction(text, h, mi):
    assert start(text) == _clk(h, mi)


@pytest.mark.parametrize("h", list(range(1, 13)))
def test_em_ponto_hour_sweep(h):
    text = f"{_art(h)} {_NUM[h]} em ponto"
    assert start(text) == _clk(h, 0)
