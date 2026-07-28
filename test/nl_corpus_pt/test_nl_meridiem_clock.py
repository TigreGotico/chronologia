# -*- coding: utf-8 -*-
"""Clock hour disambiguated by a spoken meridiem: "da manhã", "da tarde",
"da noite", "da madrugada".

The bare hour is a 12-clock; the trailing "da <parte-do-dia>" fixes which turn
of the 24-clock the speaker meant.  European Portuguese habitually voices this
period instead of am/pm, and the four words map onto the 24-clock as:

    da madrugada  -> hour as spoken   (01..05, the small hours)
    da manhã      -> hour as spoken   (06..11)
    da tarde      -> hour + 12        (13..18)
    da noite      -> hour + 12        (19..23)

The minute-wide span then takes the ordinary prefer_future roll: an hour
already past today lands tomorrow, an hour still ahead stays today.  Anchor is
Tuesday 2017-06-27 13:04, so 15:00 ("três da tarde") is still ahead and stays
on the 27th while 09:00 ("nove da manhã") has passed and rolls to the 28th.

The gold hour is computed here by the table above -- never read back from the
parser.  [[EP vs BP]]: the words and this mapping are shared by both norms;
"da manhã/tarde/noite" is the everyday spoken form on both sides of the
Atlantic, so nothing here is EP-only.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start, span

_NUM = {1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis",
        7: "sete", 8: "oito", 9: "nove", 10: "dez", 11: "onze"}

#: (period word, hour offset applied to the spoken numeral)
_PERIODS = {"madrugada": 0, "manhã": 0, "tarde": 12, "noite": 12}

#: idiomatic hour ranges per period (EP spoken usage)
_HOURS = {
    "madrugada": range(1, 6),   # 1..5
    "manhã": range(6, 12),      # 6..11
    "tarde": range(1, 7),       # 1..6  -> 13..18
    "noite": range(7, 12),      # 7..11 -> 19..23
}


def _clk(hour):
    dt = ANCHOR.replace(hour=hour, minute=0, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


def _cases():
    out = []
    for period, off in _PERIODS.items():
        for h in _HOURS[period]:
            art = "à" if h == 1 else "às"
            text = f"{art} {_NUM[h]} da {period}"
            out.append((text, _clk(h + off)))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,gold", _CASES)
def test_meridiem_hour(text, gold):
    assert start(text) == gold
    assert span(text).width == timedelta(minutes=1)


# -- fractions ride the meridiem too: "e meia" == :30, "e um quarto" == :15 --
@pytest.mark.parametrize("text,hour,minute", [
    ("às sete e meia da manhã", 7, 30),
    ("às três e meia da tarde", 15, 30),
    ("às nove e um quarto da manhã", 9, 15),
    ("às dez e meia da noite", 22, 30),
    ("às quatro e um quarto da madrugada", 4, 15),
])
def test_meridiem_fraction(text, hour, minute):
    dt = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start(text) == ad(dt)


# -- meio-dia / meia-noite: the two named clock points, with the future roll --
@pytest.mark.parametrize("text,hour,minute", [
    ("ao meio-dia", 12, 0),
    ("à meia-noite", 0, 0),
    ("ao meio-dia e meia", 12, 30),
])
def test_named_clock_points(text, hour, minute):
    dt = ANCHOR.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    assert start(text) == ad(dt)
