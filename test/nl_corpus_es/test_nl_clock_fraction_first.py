# -*- coding: utf-8 -*-
"""Fraction-first "quarter to" clock readings: "un cuarto para las cuatro"
names the fraction before the target hour ("a quarter toward four"), unlike
the hour-first subtractive "las cuatro menos cuarto" (see test_nl_clock.py).
"para" marks the toward-direction; the bare-number variant ("quince para las
cuatro") uses the same CLOCKDIR word with a plain minute count instead of a
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
    ("un cuarto para las cuatro", 3, 45),
    ("un cuarto para las diez", 9, 45),
    ("media para las cuatro", 3, 30),
])
def test_fraction_first_quarter_to(text, h, mi):
    assert start(text) == clk(h, mi)


# Bare-number variant: a plain minute count instead of a named fraction word,
# same CLOCKDIR "para" toward-direction ("quince para las cuatro" == 3:45).
@pytest.mark.parametrize("text,h,mi", [
    ("quince para las cuatro", 3, 45),
    ("veinte para las diez", 9, 40),
])
def test_fraction_first_minutes_to(text, h, mi):
    assert start(text) == clk(h, mi)


def test_fraction_first_not_a_range():
    # adversarial: this must read a clock time, not strand the fraction as
    # remainder while landing on the bare target hour (the original defect:
    # "un cuarto para las cuatro" silently read 04:00).
    assert start("un cuarto para las cuatro") == clk(3, 45)


def test_hour_first_minus_unchanged():
    # control: the pre-existing hour-first subtractive form must not regress.
    assert start("las cuatro menos cuarto") == clk(3, 45)


def test_redundant_menos_para_not_a_silent_guess():
    # "menos cuarto para las cuatro" mixes both the hour-first "menos" and the
    # fraction-first "para" markers in one non-idiomatic phrase; it must be
    # refused rather than guessed at.
    nomatch("menos cuarto para las cuatro")
