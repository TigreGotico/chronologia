# -*- coding: utf-8 -*-
"""Fraction-first "quarter to" clock readings: "um quarto para as quatro"
names the fraction before the target hour ("a quarter toward four"), unlike
the hour-first subtractive "quatro menos um quarto" (see test_nl_clock.py).
"para" marks the toward-direction; the bare-number variant ("quinze para as
quatro") uses the same CLOCKDIR word with a plain minute count instead of a
named fraction.

Gold is computed by hand: N minutes "para" (toward) hour H reads (H-1):(60-N),
the same roll-back arithmetic the hour-first "menos" form and French "moins
le quart" both use.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span, nomatch


def clk(h, mi, s=0):
    dt = ANCHOR.replace(hour=h, minute=mi, second=s, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi", [
    ("um quarto para as quatro", 3, 45),
    ("um quarto para as dez", 9, 45),
    ("meia para as quatro", 3, 30),
])
def test_fraction_first_quarter_to(text, h, mi):
    assert start(text) == clk(h, mi)


# Bare-number variant: a plain minute count instead of a named fraction word,
# same CLOCKDIR "para" toward-direction ("quinze para as quatro" == 3:45).
@pytest.mark.parametrize("text,h,mi", [
    ("quinze para as quatro", 3, 45),
    ("vinte para as dez", 9, 40),
])
def test_fraction_first_minutes_to(text, h, mi):
    assert start(text) == clk(h, mi)


def test_fraction_first_not_a_range():
    # adversarial: this must read a clock time, not strand the fraction as
    # remainder while landing on the bare target hour (the original defect:
    # "um quarto para as quatro" silently read 04:00).
    assert start("um quarto para as quatro") == clk(3, 45)


def test_hour_first_minus_unchanged():
    # control: the pre-existing hour-first subtractive form must not regress.
    assert start("duas menos um quarto") == clk(1, 45)
